from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from services.auth import get_current_user_id
from schemas.post import PostCreate, PostOut
from database.database import get_db
from database.models.post import Post


router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=PostOut)
def create_post(
    post: PostCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new post.
    Requires authentication via Bearer token.
    """
    new_post = Post(
        title=post.title,
        content=post.content,
        owner_id=user_id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    response = PostOut(
        id=new_post.id,
        title=new_post.title,
        content=new_post.content,
        owner_id=new_post.owner_id
    )

    return response
