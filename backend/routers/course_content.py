from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from agents.research_agent import run_research
from agents.author_agent import run_author_agent
from models.curriculum import Section, QuizQuestion
from models.research import ResearchDomain
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from core.database import get_db
from models.curriculum import Course

router = APIRouter()

@router.get("/admin/courses")
def get_courses(db: Session = Depends(get_db)):
    """List all courses to populate the dropdown menu."""
    courses = db.query(Course).all()
    # Return simple list for UI
    return [{"id": c.id, "title": c.title} for c in courses]

@router.get("/admin/course/{course_id}/sections")
def get_sections(course_id: int, db: Session = Depends(get_db)):
    """List sections for a specific course along with published content and quizzes."""
    sections = (
        db.query(Section)
        .options(joinedload(Section.quizzes))
        .filter(Section.course_id == course_id)
        .order_by(Section.order_index)
        .all()
    )

    payload = []
    for section in sections:
        quiz_payload = [
            {
                "id": quiz.id,
                "question": quiz.question_text,
                "correct_answer": quiz.correct_answer,
                "options": quiz.distractors or [],
            }
            for quiz in section.quizzes
        ]

        payload.append(
            {
                "id": section.id,
                "title": section.title,
                "order_index": section.order_index,
                "master_content": section.master_content,
                "key_facts": section.key_facts or {},
                "quiz_data": quiz_payload,
            }
        )

    return payload

@router.post("/admin/research")
def research_topic(topic: str):
    """Scrapes web and saves to Vector DB (KnowledgeItem)"""
    result = run_research(topic)
    return result

@router.post("/admin/draft-section-content/{section_id}")
def draft_section_content(section_id: int, db: Session = Depends(get_db)):
    """
    Returns the Content + Quizzes for the Admin to Review/Edit.
    Does NOT save to DB yet.
    """
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    # Use the search query we saved during Syllabus generation, or the title
    query = section.key_facts.get("search_query", section.title)

    # Run Graph
    result = run_author_agent(query)
    
    # Just return the result so the Frontend can display an "Edit Form"
    return {"status": "success", "data": result}

class SaveContentRequest(BaseModel):
    master_content: str
    quiz_data: List[dict]


class ResearchDomainCreate(BaseModel):
    domain: str
    label: Optional[str] = None


class ResearchDomainResponse(BaseModel):
    id: int
    domain: str
    label: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

@router.post("/admin/save-section-content/{section_id}")
def save_section_content(
    section_id: int, 
    payload: SaveContentRequest, 
    db: Session = Depends(get_db)
):
    """
    Take the finalized text and quizzes and write them to the DB.
    """
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    # 1. Save Master Content (The text)
    section.master_content = payload.master_content
    
    # 2. Save Quizzes
    # First, clear old quizzes for this section to avoid duplicates
    db.query(QuizQuestion).filter(QuizQuestion.section_id == section_id).delete()
    
    # Add the new (reviewed) questions
    for q in payload.quiz_data:
        new_q = QuizQuestion(
            section_id=section_id,
            question_text=q['question'],
            correct_answer=q['correct_answer'],
            distractors=q['options'] # Ensure your frontend sends this structure
        )
        db.add(new_q)
        
    db.commit()
    return {"status": "saved"}


@router.get(
    "/admin/research-domains",
    response_model=List[ResearchDomainResponse],
)
def list_research_domains(db: Session = Depends(get_db)):
    """Return all configured domains used by the Research Agent."""
    domains = (
        db.query(ResearchDomain)
        .order_by(ResearchDomain.is_active.desc(), ResearchDomain.domain.asc())
        .all()
    )
    return domains


@router.post(
    "/admin/research-domains",
    response_model=ResearchDomainResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_research_domain(payload: ResearchDomainCreate, db: Session = Depends(get_db)):
    normalized_domain = payload.domain.strip().lower()
    if not normalized_domain:
        raise HTTPException(status_code=400, detail="Domain cannot be empty")

    existing = (
        db.query(ResearchDomain)
        .filter(func.lower(ResearchDomain.domain) == normalized_domain)
        .first()
    )
    if existing:
        if existing.is_active:
            raise HTTPException(status_code=400, detail="Domain already exists")
        existing.is_active = True
        if payload.label:
            existing.label = payload.label
        db.commit()
        db.refresh(existing)
        return existing

    new_domain = ResearchDomain(domain=normalized_domain, label=payload.label)
    db.add(new_domain)
    db.commit()
    db.refresh(new_domain)
    return new_domain


@router.delete(
    "/admin/research-domains/{domain_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_research_domain(domain_id: int, db: Session = Depends(get_db)):
    record = db.query(ResearchDomain).filter(ResearchDomain.id == domain_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Domain not found")

    db.delete(record)
    db.commit()
    return None