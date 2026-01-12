from sqlalchemy.orm import Session
from models.curriculum import Course, Section, QuizQuestion
from models.user import User, StudentProgress
from agents.tutor_agent import run_tutor_agent

def prefetch_course_content(course_id: int, user_id: int, db: Session):
    """
    Loops through ALL sections in a course.
    Generates and caches content for the specific user context.
    """
    print(f"--- [Prefetch] Starting background generation for Course {course_id}, User {user_id} ---")
    
    # 1. Get User Profile (for Interest)
    user = db.query(User).filter(User.id == user_id).first()
    if not user: 
        return

    # 2. Get All Sections
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return
        
    for section in course.sections:
        # 3. Check if already exists (Don't waste money)
        existing_progress = db.query(StudentProgress).filter_by(
            user_id=user_id, 
            section_id=section.id
        ).first()
        
        # If it exists and has content, skip
        if existing_progress and existing_progress.personalized_content:
            continue
            
        # 4. If Master Content is missing, we can't generate
        if not section.master_content:
            print(f"Skipping Section {section.id}: No Master Content found.")
            continue

        print(f"--- [Prefetch] Generating Section {section.id} ---")

        # 5. Prepare Quiz Data
        master_quiz = db.query(QuizQuestion).filter(QuizQuestion.section_id == section.id).first()
        quiz_dict = {
            "question_text": master_quiz.question_text,
            "correct_answer": master_quiz.correct_answer,
            "distractors": master_quiz.distractors
        } if master_quiz else None

        # 6. RUN AI (This takes ~3-5 seconds per section)
        # Since this is in background, user doesn't feel the wait.
        try:
            result = run_tutor_agent(
                section.master_content, 
                quiz_dict, 
                user.interests or "General"
            )
            
            # 7. Save to DB
            if not existing_progress:
                new_progress = StudentProgress(user_id=user_id, section_id=section.id)
                db.add(new_progress)
                existing_progress = new_progress # Reference for update
            
            existing_progress.personalized_content = result['personalized_content']
            existing_progress.personalized_quiz = result['personalized_quiz']
            db.commit()
            
        except Exception as e:
            print(f"Error generating section {section.id}: {e}")
            
    print(f"--- [Prefetch] Finished Course {course_id} ---")