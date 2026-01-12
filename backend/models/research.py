from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from core.database import Base


class ResearchDomain(Base):
    __tablename__ = "research_domains"

    id = Column(Integer, primary_key=True)
    domain = Column(String, unique=True, nullable=False)
    label = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
