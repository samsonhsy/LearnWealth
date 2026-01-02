from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from agents.research_agent import run_research
from agents.author_agent import run_author_agent
from models.curriculum import Section, QuizQuestion
from sqlalchemy.orm import Session
from core.database import get_db

router = APIRouter()

@router.post("/admin/research")
def api_research_topic(topic: str):
    """Scrapes web and saves to Vector DB (KnowledgeItem)"""
    result = run_research(topic)
    return result

@router.post("/admin/draft-section-content/{section_id}")
def api_draft_section_content(section_id: int, db: Session = Depends(get_db)):
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

@router.post("/admin/save-section-content/{section_id}")
def api_save_section_content(
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