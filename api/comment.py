from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from services.auth import get_current_user_id
from services.comment import (
    get_comment_or_404,
    verify_comment_ownership,
    comment_to_schema,
    verify_post_exists,
    verify_parent_comment_exists
)
from schemas.comment import CommentCreate, CommentUpdate, CommentOut
from database.database import get_db
from database.models.comment import Comment


router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/", response_model=CommentOut)
def create_comment(
    comment: CommentCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new comment or reply.
    Requires authentication via Bearer token.
    If parent_id is provided, creates a reply to that comment.
    """
    # Verify the post exists
    verify_post_exists(db, comment.post_id)

    # If parent_id is provided, verify the parent comment exists
    if comment.parent_id is not None:
        verify_parent_comment_exists(db, comment.parent_id)

    new_comment = Comment(
        content=comment.content,
        post_id=comment.post_id,
        parent_id=comment.parent_id,
        owner_id=user_id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return comment_to_schema(new_comment)

@router.get("/", response_model=List[CommentOut])
def get_comments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all comments with pagination.
    No authentication required.
    """
    comments = db.query(Comment).offset(skip).limit(limit).all()
    return [comment_to_schema(comment) for comment in comments]

@router.get("/user/{user_id}", response_model=List[CommentOut])
def get_comments_by_user(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all comments by a specific user with pagination.
    No authentication required.
    """
    comments = db.query(Comment).filter(Comment.owner_id == user_id).offset(skip).limit(limit).all()
    return [comment_to_schema(comment) for comment in comments]

@router.get("/{comment_id}", response_model=CommentOut)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """
    Get a single comment by ID.
    No authentication required.
    """
    comment = get_comment_or_404(db, comment_id)
    return comment_to_schema(comment)

@router.put("/{comment_id}", response_model=CommentOut)
def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update a comment's content.
    Requires authentication. Only the comment owner can update.
    """
    comment = get_comment_or_404(db, comment_id)
    verify_comment_ownership(comment, user_id)

    # Update content if provided
    if comment_update.content is not None:
        comment.content = comment_update.content

    db.commit()
    db.refresh(comment)

    return comment_to_schema(comment)

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a comment.
    Requires authentication. Only the comment owner can delete.
    Deleting a parent comment will cascade delete all replies.
    """
    comment = get_comment_or_404(db, comment_id)
    verify_comment_ownership(comment, user_id)

    db.delete(comment)
    db.commit()

    return None
