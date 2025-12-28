from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    parent_id = Column(Integer, ForeignKey("posts.id"), nullable=True)

    # Relationship: post -> owner (many-to-one)
    owner = relationship("User", back_populates="posts")

    # Relationship: reply -> parent (many-to-one)
    parent = relationship("Post", remote_side=[id], back_populates="replies")

    # Relationship: parent -> replies (one-to-many)
    replies = relationship("Post", back_populates="parent")



