# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr

from core.database import get_db
from services.user_service import get_users, get_user_by_id, get_user_by_email, get_user_by_username, create_user, delete_user
from services.auth_service import get_current_user

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    interests: str

class UserOutput(BaseModel):
    username: str
    email: EmailStr
    id: int
    class Config: 
        from_attributes = True # SQLAlchemy(DB) to Pydantic(API)

@router.get("/", response_model=list[UserOutput], status_code=status.HTTP_200_OK)
def user_list(db: Session = Depends(get_db)):
    '''Retrieves a list of all users'''
    db_users = get_users(db)
    return db_users
    
@router.get("/me", response_model=UserOutput, status_code=status.HTTP_200_OK)
def current_user_info(
    user = Depends(get_current_user)
):
    '''Retrieves information about the current authenticated user'''
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def user_delete(user_id: int, db: Session = Depends(get_db)):
    '''Deletes a user by user ID'''
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    delete_user(db, user_id)
    return 
    
@router.post("/register", response_model=UserOutput, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    '''Registers a new user'''
    db_user_by_email = get_user_by_email(db=db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user_by_username = get_user_by_username(db=db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    return create_user(db=db, user=user)
