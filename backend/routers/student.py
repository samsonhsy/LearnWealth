from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from services.auth_service import get_current_user
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from models.user import StudentProgress, User
from models.curriculum import Course, Section
from services.tutor_service import prefetch_course_content 

router = APIRouter()

# --- INPUT SCHEMAS (For React JSON Body) ---

# Dashboard and Course Interaction Endpoints
@router.get("/student/courses")
def get_student_courses(db: Session = Depends(get_db), user = Depends(get_current_user)):
    """Returns list of courses with calculated progress."""
    courses = db.query(Course).all()
    result = []
    
    for c in courses:
        total = len(c.sections)
        # Find completed sections for this user in this course
        completed = db.query(StudentProgress).filter(
            StudentProgress.user_id == user.id,
            StudentProgress.is_completed == True,
            StudentProgress.section_id.in_([s.id for s in c.sections])
        ).count()
        
        pct = int((completed / total) * 100) if total > 0 else 0
        result.append({
            "id": c.id, 
            "title": c.title, 
            "description": c.description, 
            "progress": pct
        })
    return result

# get course details with sections and lock status
@router.get("/student/course/{course_id}")
def get_course_details(course_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    """Returns map of sections. Locks future sections."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    sections_data = []
    is_unlocked = True # First section is always open
    
    # Sort by order_index to ensure correct flow
    sorted_sections = sorted(course.sections, key=lambda x: x.order_index)

    for sec in sorted_sections:
        prog = db.query(StudentProgress).filter_by(user_id=user.id, section_id=sec.id).first()
        is_completed = prog.is_completed if prog else False
        
        sections_data.append({
            "id": sec.id,
            "title": sec.title,
            "is_locked": not is_unlocked, # Locked if previous wasn't unlocked
            "is_completed": is_completed
        })
        
        # Logic: If this one isn't done, lock the NEXT one.
        if not is_completed:
            is_unlocked = False 
            
    return {"course": course.title, "sections": sections_data}

# enroll in course and trigger background content generation
@router.post("/student/course/{course_id}/enroll")
def enroll_in_course(
    course_id: int, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db), 
    user = Depends(get_current_user)
):
    """Triggers background generation."""
    # Add task to background
    background_tasks.add_task(prefetch_course_content, course_id, user.id, db)
    return {"status": "enrolled", "message": "AI started generating content."}

# section content retrieval
@router.get("/student/section/{section_id}/content")
def get_section_content(
    section_id: int, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """
    Called when user clicks a lesson.
    Returns {status: 'ready', content: ...} or {status: 'processing'}
    """
    progress = db.query(StudentProgress).filter_by(user_id=user.id, section_id=section_id).first()
    
    # CASE A: Ready
    if progress and progress.personalized_content:
        return {
            "status": "ready",
            "content": progress.personalized_content,
            "quiz": progress.personalized_quiz
        }
    
    # CASE B: User forgot to Enroll, or Enroll failed. Trigger Fallback.
    # We find the course_id for this section and trigger generation now.
    section = db.query(Section).filter(Section.id == section_id).first()
    if section:
        # Re-trigger background task just in case
        background_tasks.add_task(prefetch_course_content, section.course_id, user.id, db)

    return {"status": "processing", "message": "AI is writing... please poll again in 2s"}

# quiz submission and unlocking next section
@router.post("/student/section/{section_id}/submit")
def submit_quiz(
    section_id: int, 
    correct: bool,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Unlocks the next section."""
    progress = db.query(StudentProgress).filter_by(
        user_id=user.id, 
        section_id=section_id
    ).first()
    
    if progress:
        progress.is_completed = True
        progress.quiz_score = 100 if correct else 0
        db.commit()
        return {"status": "success", "unlocked_next": True}
    
    raise HTTPException(status_code=404, detail="Progress record not found")