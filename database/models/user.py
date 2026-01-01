from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Relationship: user -> posts (one-to-many)
    posts = relationship("Post", back_populates="owner")

    # Relationship: user -> comments (one-to-many)
    comments = relationship("Comment", back_populates="owner")

