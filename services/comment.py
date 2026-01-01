from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models.comment import Comment
from database.models.post import Post
from schemas.comment import CommentOut


def get_comment_or_404(db: Session, comment_id: int) -> Comment:
    """
    Get a comment by ID or raise 404.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


def verify_comment_ownership(comment: Comment, user_id: int) -> None:
    """
    Verify that the user owns the comment, raise 403 if not.
    """
    if comment.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this comment"
        )


def comment_to_schema(comment: Comment) -> CommentOut:
    """
    Convert a Comment model to CommentOut schema.
    """
    return CommentOut(
        id=comment.id,
        content=comment.content,
        owner_id=comment.owner_id,
        post_id=comment.post_id,
        parent_id=comment.parent_id
    )


def verify_post_exists(db: Session, post_id: int) -> None:
    """
    Verify the post exists, raise 404 if not.
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")


def verify_parent_comment_exists(db: Session, parent_id: int) -> None:
    """
    Verify parent comment exists, raise 404 if not.
    """
    parent_comment = db.query(Comment).filter(Comment.id == parent_id).first()
    if not parent_comment:
        raise HTTPException(status_code=404, detail="Parent comment not found")
