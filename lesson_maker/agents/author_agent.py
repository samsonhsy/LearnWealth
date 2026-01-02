from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from core.database import SessionLocal
from models.knowledge_base import KnowledgeItem
from core.llm import get_embeddings, get_llm

class QuizQuestionSchema(BaseModel):
    question: str = Field(description="The question text")
    options: List[str] = Field(description="List of 4 options")
    correct_answer: str = Field(description="The correct option text")
    explanation: str = Field(description="Why this answer is correct")

class QuizList(BaseModel):
    questions: List[QuizQuestionSchema]

class AuthorState(TypedDict):
    # Inputs
    topic: str
    
    # Internal Data
    retrieved_facts: str
    source_urls: List[str]
    
    # Outputs
    master_content: str
    quiz_data: List[dict] # Storing as dicts for easy JSON serialization

def retrieve_node(state: AuthorState):
    """Semantic Search to get facts."""
    print(f"--- [Author] Retrieving facts for: {state['topic']} ---")
    
    session = SessionLocal()
    embeddings = get_embeddings()
    
    # Embed query
    query_vector = embeddings.embed_query(state['topic'])
    
    # Search top 5 relevant facts
    results = session.query(KnowledgeItem).order_by(
        KnowledgeItem.embedding.l2_distance(query_vector)
    ).limit(5).all()
    
    session.close()
    
    if not results:
        # Fallback if DB is empty
        return {
            "retrieved_facts": "No specific facts found.",
            "source_urls": []
        }

    # Format for LLM
    context = "\n".join([f"- {item.fact_text}" for item in results])
    sources = list(set([item.source_url for item in results]))
    
    return {"retrieved_facts": context, "source_urls": sources}

def draft_node(state: AuthorState):
    """Writes the Tutorial based on retrieved facts."""
    print("--- [Author] Drafting Content ---")
    
    llm = get_llm(temperature=0.4)
    
    prompt = f"""
    You are a Financial Course Author for Hong Kong students.
    Write a clear, educational section about: "{state['topic']}".
    
    RULES:
    1. Use ONLY these facts:
    {state['retrieved_facts']}
    
    2. Length: 150-200 words.
    3. Tone: Neutral, professional, educational.
    4. formatting: Use paragraphs.
    """
    
    response = llm.invoke(prompt)
    return {"master_content": response.content}

def quiz_node(state: AuthorState):
    """Generates 1 to 3 Questions based on the Draft."""
    print("--- [Author] Generating Quiz ---")
    
    llm = get_llm(temperature=0, model_name="gpt-4o-mini")
    structured_llm = llm.with_structured_output(QuizList)
    
    prompt = f"""
    Based STRICTLY on the tutorial text below, generate 2 Multiple Choice Questions.
    
    TUTORIAL:
    "{state['master_content']}"
    
    REQUIREMENTS:
    - Questions must test understanding of the concepts in the text.
    - 4 options per question.
    - Identify the correct answer.
    """
    
    result = structured_llm.invoke(prompt)
    
    clean_quizzes = [q.model_dump() for q in result.questions]
    
    return {"quiz_data": clean_quizzes}

workflow = StateGraph(AuthorState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("draft", draft_node)
workflow.add_node("quiz", quiz_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "draft")
workflow.add_edge("draft", "quiz")
workflow.add_edge("quiz", END)

author_app = workflow.compile()

# Helper Function for API
def run_author_agent(topic: str):
    """Entry point for the API"""
    initial_state = {
        "topic": topic,
        "retrieved_facts": "",
        "source_urls": [],
        "master_content": "",
        "quiz_data": []
    }
    return author_app.invoke(initial_state)