from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from core.database import Base

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)          # e.g. "Financial Basics 101"
    description = Column(Text)
    level = Column(String)          # "Beginner", "Intermediate"
    
    # Relationship to sections
    sections = relationship("Section", back_populates="course")

class Section(Base):
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)          # e.g. "What is Interest?"
    order_index = Column(Integer)   # 1, 2, 3...
    
    # The "Master Content" (Neutral, Fact-checked text)
    master_content = Column(Text)
    
    # Key facts for AI reference (e.g. {"rate": 0.05})
    key_facts = Column(JSON)
    
    course = relationship("Course", back_populates="sections")
    quizzes = relationship("QuizQuestion", back_populates="section")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id"))
    
    question_text = Column(Text)
    correct_answer = Column(String)     
    distractors = Column(JSON) # List of incorrect options
    
    section = relationship("Section", back_populates="quizzes")