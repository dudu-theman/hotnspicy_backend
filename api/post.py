from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from services.auth import get_current_user_id
from services.post import get_post_or_404, verify_post_ownership, post_to_schema
from schemas.post import PostCreate, PostUpdate, PostOut
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

    return post_to_schema(new_post)

@router.get("/", response_model=List[PostOut])
def get_posts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all posts with pagination.
    No authentication required.
    """
    posts = db.query(Post).offset(skip).limit(limit).all()
    return [post_to_schema(post) for post in posts]

@router.get("/user/{user_id}", response_model=List[PostOut])
def get_posts_by_user(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all posts by a specific user with pagination.
    No authentication required.
    """
    posts = db.query(Post).filter(Post.owner_id == user_id).offset(skip).limit(limit).all()
    return [post_to_schema(post) for post in posts]

@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """
    Get a single post by ID.
    No authentication required.
    """
    post = get_post_or_404(db, post_id)
    return post_to_schema(post)

@router.put("/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update a post (title and/or content).
    Requires authentication. Only the post owner can update.
    """
    post = get_post_or_404(db, post_id)
    verify_post_ownership(post, user_id)

    # Update fields if provided
    if post_update.title is not None:
        post.title = post_update.title
    if post_update.content is not None:
        post.content = post_update.content

    db.commit()
    db.refresh(post)

    return post_to_schema(post)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a post.
    Requires authentication. Only the post owner can delete.
    """
    post = get_post_or_404(db, post_id)
    verify_post_ownership(post, user_id)

    db.delete(post)
    db.commit()

    return None
