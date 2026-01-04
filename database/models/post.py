from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, and_
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship: post -> comments (one-to-many)
    comments = relationship("Comment", back_populates="post")

    # Relationship: post -> top level comments only (one-to-many, view only)
    top_level_comments = relationship(
        "Comment",
        primaryjoin="and_(Post.id==Comment.post_id, Comment.parent_id==None)",
        viewonly=True
    )

    # Relationship: post -> owner (many-to-one)
    owner = relationship("User", back_populates="posts")





