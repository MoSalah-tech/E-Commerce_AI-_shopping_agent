# --------------- Auth models ---------------
from pydantic import BaseModel

class User(BaseModel):
    username: str
    full_name: str | None = None
    email: str | None = None
    disabled: bool = False

class UserInDB(User):
    hashed_password: str



class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str | None = None
    email: str | None = None