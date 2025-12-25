from pydantic import BaseModel
from schemas.token import Token

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    identifier: str
    password: str

class UserWithToken(BaseModel):
    user: UserOut
    token: Token