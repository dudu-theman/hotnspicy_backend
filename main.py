from fastapi import FastAPI

from api.auth import router as auth_router
from api.post import router as post_router
from database import Base, engine
# Import models so SQLAlchemy knows about them before creating tables
from database.models import User, Post, Comment  # noqa: F401

app = FastAPI()
app.include_router(auth_router)
app.include_router(post_router)

# Create database tables
Base.metadata.create_all(bind=engine)



