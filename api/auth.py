from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from services.auth import hash_password, verify_password, create_access_token, get_current_user_id
from schemas.user import UserCreate, UserLogin, UserWithToken, UserOut
from schemas.token import Token

from database.database import get_db

from database.models.user import User



router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserWithToken)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": str(new_user.id)})

    user_out = UserOut(id=new_user.id, username=new_user.username, email=new_user.email)
    token = Token(access_token=access_token, token_type="bearer")
    response = UserWithToken(user=user_out, token=token)

    return response

@router.post("/token", response_model=Token)
def token(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        or_(
            User.username == user.identifier,
            User.email == user.identifier
        )
    ).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_access_token(data={"sub": str(db_user.id)})
    response = Token(access_token=access_token, token_type="bearer")

    return response

@router.post("/refresh", response_model=Token)
def refresh(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Refresh an access token.
    Requires a valid Bearer token in the Authorization header.
    Returns a new access token.
    """
    # Verify the user still exists
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    # Create a new access token
    access_token = create_access_token(data={"sub": str(user_id)})
    response = Token(access_token=access_token, token_type="bearer")

    return response

