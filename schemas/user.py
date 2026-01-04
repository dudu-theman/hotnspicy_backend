from pydantic import BaseModel, ConfigDict
from schemas.token import Token
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    created_at: datetime

class UserLogin(BaseModel):
    identifier: str
    password: str

class UserWithToken(BaseModel):
    user: UserOut
    token: Token