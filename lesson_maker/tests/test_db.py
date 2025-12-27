import time
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector

# 1. Connection String
# format: postgresql://user:password@localhost:port/dbname
DATABASE_URL = "postgresql://admin:password123@localhost:5432/financial_db"

# 2. Connect to the DB
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# 3. Define a Table (Model)
class Knowledge(Base):
    __tablename__ = 'knowledge'
    id = Column(Integer, primary_key=True)
    content = Column(String)
    # This is the SPECIAL part. We define a vector with 3 dimensions for this test.
    # (In real AI, OpenAI uses 1536 dimensions)
    embedding = Column(Vector(3))

def main():
    # Wait a moment for Docker to fully start
    print("Connecting to Docker Database...")
    time.sleep(2)
    
    # 4. Enable the Extension (CRITICAL STEP)
    # We must tell Postgres to turn on the AI features.
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    # 5. Create the tables
    Base.metadata.drop_all(engine) # Reset for testing
    Base.metadata.create_all(engine)
    print("Table created!")

    # 6. Insert Mock Data
    session = Session()
    
    # Imagine:
    # Vector [1, 0, 0] = "Finance"
    # Vector [0, 1, 0] = "Biology"
    # Vector [0, 0, 1] = "History"
    
    data1 = Knowledge(content="Compound Interest info", embedding=[0.9, 0.1, 0.0]) # Mostly Finance
    data2 = Knowledge(content="Cell Division info", embedding=[0.0, 0.9, 0.1])     # Mostly Biology
    
    session.add_all([data1, data2])
    session.commit()
    print("Data inserted!")

    # 7. The Search (The "Hackathon Winning" Feature)
    # User asks a Finance question. Let's look for vector [1, 0, 0]
    user_query_vector = [1, 0, 0]
    
    # We use L2 Distance (Euclidean) operator: <->
    # "Find items where embedding is closest to my query"
    results = session.query(Knowledge).order_by(
        Knowledge.embedding.l2_distance(user_query_vector)
    ).limit(1).all()

    print(f"\nUser asked about Finance ({user_query_vector})")
    print(f"Database recommended: '{results[0].content}' with vector {results[0].embedding}")
    
    session.close()

if __name__ == "__main__":
    main()