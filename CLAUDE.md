# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

**Local development** (requires PostgreSQL running):
```bash
uvicorn main:app --reload
```

**Docker Compose** (recommended - includes PostgreSQL):
```bash
docker-compose up
```

The API will be available at http://localhost:8000 with interactive docs at http://localhost:8000/docs.

## Development Commands

**Build Docker image**:
```bash
docker build -t hotnspicy_app .
```

**Start services** (PostgreSQL + app):
```bash
docker-compose up
```

**Stop services**:
```bash
docker-compose down
```

**Install dependencies** (local development):
```bash
pip install -r requirements.txt
```

**Testing**: Use the interactive Swagger UI at http://localhost:8000/docs for endpoint testing. No test framework (pytest) or linters (black, flake8) are currently configured.

## Database Setup

This application uses PostgreSQL. Connection configured via environment variables in `.env`:
- `DATABASE_URL`: PostgreSQL connection string (format: `postgresql+psycopg2://user:password@host:port/dbname`)
- `SECRET_KEY`: JWT signing key
- `ALGORITHM`: JWT algorithm (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

Tables are auto-created via `Base.metadata.create_all(bind=engine)` in `main.py` when the app starts.

Docker Compose provides a pre-configured PostgreSQL instance. See `docker-compose.yml` for connection details.

## Architecture

### Layer Structure

The application follows a clean architecture with clear separation of concerns. All modules are in the root directory (not under an `app/` package):

**API Layer** (`api/`): FastAPI routers that handle HTTP requests/responses
- `auth.py` - authentication endpoints (register, token, refresh)
- `post.py` - post CRUD endpoints (create, read, update, delete)
- `comment.py` - comment CRUD endpoints with nested reply support

**Service Layer** (`services/`): Business logic and operations
- `auth.py`: Password hashing (Argon2), JWT token creation/verification
- `post.py`: Post business logic and helper functions
- `comment.py`: Comment business logic with nested reply support

**Schema Layer** (`schemas/`): Pydantic models for request/response validation
- `user.py`: UserCreate, UserOut, UserLogin, UserWithToken
- `token.py`: Token, TokenData
- `post.py`: PostCreate, PostUpdate, PostOut
- `comment.py`: CommentCreate, CommentUpdate, CommentOut

**Database Layer** (`database/`):
- `database.py`: SQLAlchemy engine, session factory, and Base class
- `models/user.py`: User model with username, email, hashed_password
- `models/post.py`: Post model with title, content, owner_id (foreign key to users)
- `models/comment.py`: Comment model with nested replies (parent_id, cascade delete)

**Core** (`core/`):
- `config.py`: Pydantic Settings for environment variables

**Main Application** (`main.py`): FastAPI app initialization, router registration, and database table creation

### Authentication Flow

The application uses JWT-based authentication with the following flow:

1. **Registration** (`POST /auth/register`): Creates new user with Argon2-hashed password, returns both user details and access token
2. **Login** (`POST /auth/token`): Accepts username OR email in `identifier` field, returns JWT access token
3. **Token Refresh** (`POST /auth/refresh`): Validates current token and issues new token with extended expiration
4. Password verification uses `passlib` with Argon2 scheme
5. Tokens are signed with HS256 algorithm and include user ID in the "sub" claim

**Authentication Dependency**: Endpoints requiring authentication use `user_id: int = Depends(get_current_user_id)`, which:
- Extracts the Bearer token from the Authorization header via `HTTPBearer()`
- Verifies the token signature and expiration via `verify_access_token()`
- Returns the authenticated user's ID for use in the endpoint

### Database Session Management

Uses dependency injection pattern for database sessions:
- `get_db()` generator in `database.py` provides session per request
- All endpoints use `db: Session = Depends(get_db)` for database access
- Sessions automatically close after request completes

### Database Relationships

**User → Posts** (one-to-many): Users can create multiple posts
- `User.posts` relationship links to all posts owned by the user
- `Post.owner` back-reference to the user

**User → Comments** (one-to-many): Users can create multiple comments
- `User.comments` relationship links to all comments owned by the user
- `Comment.owner` back-reference to the user

**Post → Comments** (one-to-many): Posts can have multiple comments
- `Post.comments` relationship links to all comments on the post
- `Post.top_level_comments` view-only relationship filters comments where `parent_id` is None
- `Comment.post` back-reference to the post

**Comment → Comment** (self-referential): Comments can have nested replies
- `Comment.parent` many-to-one relationship to parent comment
- `Comment.replies` one-to-many relationship with cascade delete (`cascade="all, delete-orphan"`)
- Deleting a parent comment automatically deletes all nested replies

### Key Design Patterns

**Flexible Login**: The `/auth/token` endpoint accepts either username or email via the `identifier` field, using SQLAlchemy's `or_()` to query both columns.

**Password Security**: Argon2 hashing (considered more secure than bcrypt) is used via passlib's CryptContext.

**JWT Structure**: Tokens include expiration (`exp`) and subject (`sub` containing user ID) claims.

**Nested Comments**: Comments support `parent_id` for threaded discussions. Deleting a parent comment cascade deletes all replies.

**Pagination**: All list endpoints support `skip` and `limit` query parameters (default limit: 100).

**Ownership Authorization**: POST/PUT/DELETE endpoints verify resource ownership and return 403 if the authenticated user is not the owner. Helper functions like `verify_post_ownership()` and `verify_comment_ownership()` in the service layer handle this logic.

**Helper Functions Pattern**: Service layer modules (`services/post.py`, `services/comment.py`) contain reusable helper functions:
- `get_post_or_404()`, `get_comment_or_404()`: Fetch resources or raise 404
- `verify_post_ownership()`, `verify_comment_ownership()`: Check ownership or raise 403
- `post_to_schema()`, `comment_to_schema()`: Convert ORM models to Pydantic schemas
- `verify_post_exists()`, `verify_parent_comment_exists()`: Validate foreign key references

## API Documentation

Comprehensive API documentation with 18 endpoints is available in `api/documentation.txt`, including:
- Authentication endpoints (register, token, refresh)
- Post CRUD operations
- Comment CRUD operations with nested replies
- cURL examples for all endpoints
- Error response formats

Interactive testing available at http://localhost:8000/docs (Swagger UI).

## Current State

Authentication, posts, and comments are fully implemented with CRUD operations. Comments support nested replies with cascade deletion.

## Dependencies

Key packages:
- FastAPI + Uvicorn: Web framework and ASGI server
- SQLAlchemy: ORM for PostgreSQL
- Pydantic + pydantic-settings: Validation and configuration
- python-jose: JWT handling
- passlib + argon2-cffi: Password hashing
- psycopg2-binary: PostgreSQL adapter
