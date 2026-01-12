# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
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
async def user_list(db:AsyncSession = Depends(get_db)):
    '''Retrieves a list of all users'''
    db_users = await get_users(db)
    return db_users
    
@router.get("/me", response_model=UserOutput, status_code=status.HTTP_200_OK)
async def current_user_info(
    user = Depends(get_current_user)
):
    '''Retrieves information about the current authenticated user'''
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def user_delete(user_id: int, db: AsyncSession = Depends(get_db)):
    '''Deletes a user by user ID'''
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await delete_user(db, user_id)
    return 
    
@router.post("/register", response_model=UserOutput, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    '''Registers a new user'''
    db_user_by_email = await get_user_by_email(db=db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user_by_username = await get_user_by_username(db=db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    return await create_user(db=db, user=user)
