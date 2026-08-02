from datetime import timedelta
from fastapi import APIRouter, Depends, Form, HTTPException, status

from app.auth.jwt import create_access_token
from app.auth.db import get_user
from app.auth.security import verify_password, hash_password
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth.models import UserCreate
from app.core.database import get_pool
from app.core.rate_limit import auth_rate_limit

router = APIRouter()


# ----- custom login form (replaces OAuth2PasswordRequestForm) -----
class LoginForm:
    def __init__(self, username: str = Form(...), password: str = Form(...)):
        self.username = username
        self.password = password


@router.post("/register", status_code=201, dependencies=[Depends(auth_rate_limit)])
async def register(user_data: UserCreate):
    """Create a new user (use from Swagger)."""
    async with get_pool().connection() as conn:
        row = await conn.execute(
            "SELECT 1 FROM users WHERE username = %s;",
            (user_data.username,)
        )
        if await row.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        hashed = hash_password(user_data.password)
        await conn.execute(
            """
            INSERT INTO users (username, full_name, email, hashed_password, disabled)
            VALUES (%s, %s, %s, %s, FALSE);
            """,
            (user_data.username, user_data.full_name, user_data.email, hashed),
        )

    return {"message": f"User '{user_data.username}' created successfully"}


@router.post("/token", dependencies=[Depends(auth_rate_limit)])
async def login(form_data: LoginForm = Depends()):
    user = await get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}