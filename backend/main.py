from fastapi import FastAPI
from routers import auth, user, syllabus, course_content    


app = FastAPI(title="WealthLearn-Backend API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the WealthLearn-backend API!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "learnwealth-backend"}

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/users", tags=["User"])
app.include_router(syllabus.router, prefix="/syllabus", tags=["Syllabus"])
app.include_router(course_content.router, prefix="/course-content", tags=["Course Content"])

