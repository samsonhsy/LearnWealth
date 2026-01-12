from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, func, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
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
    progress = relationship("StudentProgress", back_populates="user")

class StudentProgress(Base):
    __tablename__ = "student_progress"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    section_id = Column(Integer, ForeignKey("sections.id"))
    
    # Status
    is_completed = Column(Boolean, default=False)
    quiz_score = Column(Integer, default=0)
    
    # THE CACHE: Save the AI's output here so we load it instantly next time
    personalized_content = Column(Text) 
    personalized_quiz = Column(JSON) 
    
    user = relationship("User", back_populates="progress")