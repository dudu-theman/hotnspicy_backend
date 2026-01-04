from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models.post import Post
from schemas.post import PostOut


def get_post_or_404(db: Session, post_id: int) -> Post:
    """
    Get a post by ID or raise 404.
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


def verify_post_ownership(post: Post, user_id: int) -> None:
    """
    Verify that the user owns the post, raise 403 if not.
    """
    if post.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this post"
        )


def post_to_schema(post: Post) -> PostOut:
    """
    Convert a Post model to PostOut schema.
    Calculates comment_count from the comments relationship.
    """
    post_out = PostOut.model_validate(post)
    post_out.comment_count = len(post.comments)
    return post_out
