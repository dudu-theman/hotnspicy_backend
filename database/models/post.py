from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationship: post -> comments (one-to-many)
    comments = relationship("Comment", back_populates="post")

    # Relationship: post -> owner (many-to-one)
    owner = relationship("User", back_populates="posts")





