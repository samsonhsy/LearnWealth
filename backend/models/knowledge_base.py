from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
from core.database import Base

class KnowledgeItem(Base):
    __tablename__ = "knowledge_item"

    id = Column(Integer, primary_key=True)
    topic = Column(String)              
    fact_text = Column(Text)            
    source_url = Column(String)
    
    # "all-MiniLM-L6-v2" uses 384 dimensions
    embedding = Column(Vector(384)) 


