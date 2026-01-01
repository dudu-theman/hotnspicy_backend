from pydantic import BaseModel
from typing import Optional

class CommentCreate(BaseModel):
    content: str
    post_id: int
    parent_id: Optional[int] = None

class CommentUpdate(BaseModel):
    content: Optional[str] = None

class CommentOut(BaseModel):
    id: int
    content: str
    owner_id: int
    post_id: int
    parent_id: Optional[int] = None
    class Config:
        from_attributes = True
