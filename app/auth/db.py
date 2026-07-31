# app/auth/db.py
import psycopg.rows
from app.core.database import get_pool
from app.auth.models import UserInDB

async def get_user(username: str) -> UserInDB | None:
    async with get_pool().connection() as conn:
        # Make this connection return dict‑like rows
        conn.row_factory = psycopg.rows.dict_row

        row = await conn.execute(
            "SELECT username, full_name, email, disabled, hashed_password FROM users WHERE username = %s;",
            (username,)
        )
        record = await row.fetchone()
        if record is None:
            return None
        return UserInDB(
            username=record["username"],
            full_name=record["full_name"],
            email=record["email"],
            disabled=record["disabled"],
            hashed_password=record["hashed_password"],
        )