from core.database import init_db

from models.knowledge_base import KnowledgeItem
from models.curriculum import Course, Section, QuizQuestion
from models.user import User

def main():
    init_db()
    print("Database Initialized Successfully!")

if __name__ == "__main__":
    main()