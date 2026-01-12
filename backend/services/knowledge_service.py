from core.database import SessionLocal
from models.knowledge import KnowledgeItem
from core.llm import get_embeddings 

def search_knowledge_base(query: str, limit: int = 1):
    """
    Business Logic: Semantic Search
    """
    session = SessionLocal()
    embeddings_model = get_embeddings()
    
    try:
        query_vector = embeddings_model.embed_query(query)
        
        results = session.query(KnowledgeItem).order_by(
            KnowledgeItem.embedding.l2_distance(query_vector)
        ).limit(limit).all()
        
        return results
    finally:
        session.close()