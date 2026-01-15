from typing import Optional
from pydantic import BaseModel, EmailStr

from sqlalchemy.orm import Session
from sqlalchemy.future import select

from models.user import User

from core.security import get_pwd_hash

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

def get_users(db: Session) -> Optional[list[User]]:
    result = db.execute(select(User))
    return result.scalars().all()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    result = db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    result = db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    result = db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_pwd = get_pwd_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_pwd=hashed_pwd, interests=user.interests)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.execute(select(User).filter(User.id == user_id)).scalars().first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return
