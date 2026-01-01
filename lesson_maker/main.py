from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.database import get_db
from app.routers import admin, auth, users, collections
from app.s3.s3_bucket import check_storage_health
from app.services.auth_service import get_current_admin_user

app = FastAPI(title="WealthLearn-Backend API")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the WealthLearn-backend API!"}

app.include_router(auth.router, prefix="/syllabus", tags=["Syllabus"])

