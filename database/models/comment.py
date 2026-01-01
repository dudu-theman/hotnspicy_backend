from database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True, index=True)

    # Relationship: comment -> owner (many-to-one)
    owner = relationship("User", back_populates ="comments")

    # Relationship: comment -> post (many-to-one)
    post = relationship("Post", back_populates="comments")

    # Relationship: reply -> parent (many-to-one)
    parent = relationship("Comment", remote_side=[id], back_populates="replies")

    # Relationship: parent -> replies (one-to-many)
    replies = relationship("Comment", back_populates="parent", cascade="all, delete-orphan")




