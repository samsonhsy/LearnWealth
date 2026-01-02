from fastapi import APIRouter, Depends
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

@router.post("/admin/generate-section-content/{section_id}")
def api_generate_section(section_id: int, db: Session = Depends(get_db)):
    """Generates Master Content and Quizzes for a Section"""
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        return {"error": "Section not found"}
    
    # Use the search query we saved during Syllabus generation, or the title
    query = section.key_facts.get("search_query", section.title)

    # Run Graph
    result = run_author_agent(query)
    
    # Save Content
    section.master_content = result['master_content']
    
    # Save Quizzes (Loop through the list)
    # First, delete old ones
    db.query(QuizQuestion).filter(QuizQuestion.section_id == section_id).delete()
    
    for q in result['quiz_data']:
        new_q = QuizQuestion(
            section_id=section_id,
            question_text=q['question'],
            correct_answer=q['correct_answer'],
            distractors=q['options'] 
        )
        db.add(new_q)
        
    db.commit()
    return {"status": "success", "data": result}