from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, func
from core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)

    hashed_pwd = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Profile for Personalization
    interests = Column(String)       # "Science, Gaming"
    learning_style = Column(String)  # "Visual", "Text"
    
    account_tier = Column(String, default="free")

    # Progress Tracking
    completed_sections = Column(JSON) 