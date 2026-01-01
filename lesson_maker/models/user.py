from sqlalchemy import Column, Integer, String, JSON
from core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    
    # Profile for Personalization
    interests = Column(String)       # "Science, Gaming"
    learning_style = Column(String)  # "Visual", "Text"
    
    # Progress Tracking
    completed_sections = Column(JSON) 