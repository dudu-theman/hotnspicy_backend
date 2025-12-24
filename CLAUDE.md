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
- `auth.py` - authentication endpoints (register, token)

**Service Layer** (`services/`): Business logic and operations
- `auth.py`: Password hashing (Argon2), JWT token creation/verification
- `post.py`: Empty, ready for post-related business logic

**Schema Layer** (`schemas/`): Pydantic models for request/response validation
- `user.py`: UserCreate, UserOut, UserLogin
- `token.py`: Token, TokenData
- `post.py`: PostCreate, PostOut

**Database Layer** (`database/`):
- `database.py`: SQLAlchemy engine, session factory, and Base class
- `models/user.py`: User model with username, email, hashed_password
- `models/post.py`: Post model with title, content, owner_id (foreign key to users)

**Core** (`core/`):
- `config.py`: Pydantic Settings for environment variables

**Main Application** (`main.py`): FastAPI app initialization, router registration, and database table creation

### Authentication Flow

The application uses JWT-based authentication with the following flow:

1. **Registration** (`POST /auth/register`): Creates new user with Argon2-hashed password
2. **Login** (`POST /auth/token`): Accepts username OR email in `identifier` field, returns JWT access token
3. Password verification uses `passlib` with Argon2 scheme
4. Tokens are signed with HS256 algorithm and include user ID in the "sub" claim

### Database Session Management

Uses dependency injection pattern for database sessions:
- `get_db()` generator in `database.py` provides session per request
- All endpoints use `db: Session = Depends(get_db)` for database access
- Sessions automatically close after request completes

### Key Design Patterns

**Flexible Login**: The `/auth/token` endpoint accepts either username or email via the `identifier` field, using SQLAlchemy's `or_()` to query both columns.

**Password Security**: Argon2 hashing (considered more secure than bcrypt) is used via passlib's CryptContext.

**JWT Structure**: Tokens include expiration (`exp`) and subject (`sub` containing user ID) claims.

## Current State

Authentication is fully implemented. Post functionality has models and schemas defined but no API endpoints or service logic yet.

## Dependencies

Key packages:
- FastAPI + Uvicorn: Web framework and ASGI server
- SQLAlchemy: ORM for PostgreSQL
- Pydantic + pydantic-settings: Validation and configuration
- python-jose: JWT handling
- passlib + argon2-cffi: Password hashing
- psycopg2-binary: PostgreSQL adapter
