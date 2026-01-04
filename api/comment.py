from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from services.auth import get_current_user_id
from services.comment import (
    get_comment_or_404,
    verify_comment_ownership,
    comment_to_schema
)
from schemas.comment import ReplyCreate, CommentUpdate, CommentOut
from database.database import get_db
from database.models.comment import Comment


router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/{comment_id}/replies", response_model=CommentOut)
def create_reply(
    comment_id: int,
    reply: ReplyCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a reply to a comment.
    Requires authentication via Bearer token.
    """
    # Verify the parent comment exists
    parent_comment = get_comment_or_404(db, comment_id)

    new_reply = Comment(
        content=reply.content,
        post_id=parent_comment.post_id,
        parent_id=comment_id,
        owner_id=user_id
    )

    db.add(new_reply)
    db.commit()
    db.refresh(new_reply)

    return comment_to_schema(new_reply)

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

@router.get("/{comment_id}/replies", response_model=CommentOut)
def get_comment_with_replies(comment_id: int, db: Session = Depends(get_db)):
    """
    Get a comment with a shallow tree of replies (exactly 1 layer deep).
    No authentication required.
    """
    # Get the parent comment
    comment = get_comment_or_404(db, comment_id)

    # Get direct replies to this comment
    replies = db.query(Comment).filter(Comment.parent_id == comment_id).all()

    # Build the comment schema with replies
    comment_out = comment_to_schema(comment)
    comment_out.replies = [comment_to_schema(reply) for reply in replies]

    return comment_out

@router.patch("/{comment_id}", response_model=CommentOut)
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