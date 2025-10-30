from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, Schemas, crud
from database import get_db
from passlib.context import CryptContext
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# Password hashing context
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],  # Preference for argon2, fallback to bcrypt
    deprecated="auto"
)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# ---------------------------
# Create new user
# ---------------------------



@router.post("/", response_model=Schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: Schemas.UserCreate, db: Session = Depends(get_db)):
    # Check existing user by email
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash the incoming plain password
    hashed_pw = get_password_hash(user.password)

    # Pass the hashed password into crud.create_user
    new_user = crud.create_user(db=db, user=user, hashed_password=hashed_pw)

    return new_user


# ---------------------------
# Get all users
# ---------------------------
@router.get("/", response_model=List[Schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users


# ---------------------------
# Get user by ID
# ---------------------------
@router.get("/{user_id}", response_model=Schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# ---------------------------
# Update user
# ---------------------------
@router.put("/{user_id}", response_model=Schemas.UserResponse)
def update_user(user_id: int, user_update: Schemas.UserUpdate, db: Session = Depends(get_db)):
    updated_user = crud.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


# ---------------------------
# Delete user
# ---------------------------
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
