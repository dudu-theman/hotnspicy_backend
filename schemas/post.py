from pydantic import BaseModel
from typing import Optional

class PostCreate(BaseModel):
    title: str
    content: str
    parent_id: Optional[int] = None

class PostOut(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int
    parent_id: Optional[int] = None
    class Config:
        from_attributes = True