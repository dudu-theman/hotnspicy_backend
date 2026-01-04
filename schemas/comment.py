from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class CommentCreate(BaseModel):
    content: str

class ReplyCreate(BaseModel):
    content: str

class CommentUpdate(BaseModel):
    content: Optional[str] = None

class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    owner_id: int
    post_id: int
    parent_id: Optional[int] = None
    created_at: datetime
    replies: List["CommentOut"] = []

CommentOut.model_rebuild()
