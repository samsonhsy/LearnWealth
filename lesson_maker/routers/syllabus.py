# # app/routers/admin_key.py
from fastapi import APIRouter, Depends, HTTPException, status

from agents.syllabus_agent.py import generate_syllabus
from models.curriculum import Course, Section
from sqlalchemy.orm import Session
from core.database import get_db

router = APIRouter()

@router.post("/admin/generate-syllabus")
def api_generate_syllabus(topic: str):
    """AI brainstorms the syllabus structure."""
    draft = generate_syllabus(topic)
    return draft

@router.post("/admin/create-course")
def api_create_course(course_data: dict, db: Session = Depends(get_db)):
    """Admin approves and saves to DB."""
    
    new_course = Course(
        title=course_data['course_title'],
        description=course_data['course_description'],
        level="Beginner"
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    # Create Sections
    for index, sec in enumerate(course_data['sections']):
        new_section = Section(
            course_id=new_course.id,
            title=sec['title'],
            order_index=index + 1,
            # We store the search query temporarily in key_facts or a new column
            # so the Research Agent knows what to search next.
            key_facts={"search_query": sec['search_query']},
            master_content="" # Researcher will fill this
        )
        db.add(new_section)
    
    db.commit()
    return {"status": "success", "course_id": new_course.id}