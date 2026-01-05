from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth import router as auth_router
from api.post import router as post_router
from api.comment import router as comment_router
from database import Base, engine
# Import models so SQLAlchemy knows about them before creating tables
from database.models import User, Post, Comment  # noqa: F401

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth_router)
app.include_router(post_router)
app.include_router(comment_router)

# Create database tables
Base.metadata.create_all(bind=engine)



