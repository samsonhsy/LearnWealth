import json
from typing import TypedDict, List

from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from core.llm import get_llm, get_embeddings
from core.database import SessionLocal
from models.knowledge_base import KnowledgeItem
from models.research import ResearchDomain

# Default fallback domains if the admin has not configured any yet
DEFAULT_SAFE_DOMAINS = [
    "ctflife.com.hk",
    "hkma.gov.hk",
    "ifec.org.hk",
    "mpfa.org.hk",
]


def load_safe_domains() -> List[str]:
    """Fetch the latest domains from the DB, fallback to defaults."""
    session = SessionLocal()
    try:
        records = (
            session.query(ResearchDomain)
            .filter(ResearchDomain.is_active == True)  # noqa: E712
            .order_by(ResearchDomain.domain.asc())
            .all()
        )
        if records:
            return [record.domain for record in records]
    finally:
        session.close()

    return DEFAULT_SAFE_DOMAINS

class ResearchState(TypedDict):
    topic: str                  # e.g. MPF in Hong Kong""
    raw_content: str            # Data found from Search
    extracted_facts: List[dict] # Cleaned JSON data
    logs: list                  # List of logs
    allowed_domains: List[str]

def search_node(state: ResearchState) -> ResearchState:
    """Uses Tavily to find information on trusted domains. Return combined raw content."""
    print(f"--- SEARCHING: {state['topic']} ---")
    
    tavily = TavilySearch(
        max_results=3,
        include_domains=state["allowed_domains"]
    )
    results = tavily.invoke(state['topic'])['results']
    # print("--- SEARCH RESULTS ---")
    # print(results)

    # Combine results into one big string for the LLM to read
    combined_content = ""
    for res in results:
        combined_content += f"Source: {res['url']}\nContent: {res['content']}\n\n"
        
    return {"raw_content": combined_content}


def extraction_node(state: ResearchState) -> ResearchState:
    """Uses LLM to read the raw text and pick out FACTS."""
    print("--- EXTRACTING FACTS ---")
    # github models    
    llm = get_llm()

    # STRUCTURED OUTPUT: Force the AI to give us JSON, not text.
    class FactSchema(BaseModel):
        fact: str = Field(description="A concise financial rule, rate, concept or definition.")
        source_url: str = Field(description="The URL this fact came from.")
        
    class FactList(BaseModel):
        facts: List[FactSchema]

    structured_llm = llm.with_structured_output(FactList)
    
    # Prompt
    system_msg = """You are a Data Curator for a Financial Education App.
    Read the provided raw content. Extract key financial concepts, terms and definitions.
    Ignore marketing fluff. Return a clean list of facts."""
    
    response = structured_llm.invoke(f"{system_msg}\n\nRAW CONTENT:\n{state['raw_content']}")
    
    # Convert Pydantic models to normal dicts
    clean_facts = [fact.model_dump() for fact in response.facts]
    print(f"--- EXTRACTED {len(clean_facts)} FACTS ---\n")
    print(json.dumps(clean_facts, indent=2))

    return {"extracted_facts": clean_facts}

def save_node(state: ResearchState) -> ResearchState:
    print("--- SAVING (Using Local Embeddings) ---")
    session = SessionLocal()
    
    # FREE LOCAL EMBEDDINGS
    embeddings_model = get_embeddings()
    
    saved_count = 0
    for item in state['extracted_facts']:
        # This runs on CPU
        vector = embeddings_model.embed_query(item['fact'])
        
        new_entry = KnowledgeItem(
            topic=state['topic'],
            fact_text=item['fact'],
            source_url=item['source_url'],
            embedding=vector
        )
        session.add(new_entry)
        saved_count += 1
        
    session.commit()
    session.close()
    return {"logs": [f"Saved {saved_count} items"]}

# BUILD THE GRAPH
workflow = StateGraph(ResearchState)

workflow.add_node("search", search_node)
workflow.add_node("extract", extraction_node)
workflow.add_node("save", save_node)

workflow.set_entry_point("search")
workflow.add_edge("search", "extract")
workflow.add_edge("extract", "save")
workflow.add_edge("save", END)

research_app = workflow.compile()

def run_research(topic: str) -> dict:
    """Runs the Research Agent workflow."""
    safe_domains = load_safe_domains()
    initial_state: ResearchState = {
        "topic": topic,
        "raw_content": "",
        "extracted_facts": [],
        "logs": [],
        "allowed_domains": safe_domains,
    }
    
    final_state = research_app.invoke(initial_state)
    return {
        "status": "completed",
        "topic": topic,
        "facts_saved": len(final_state['extracted_facts']),
        "logs": final_state['logs']
    }