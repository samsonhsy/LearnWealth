import os
import json
from typing import TypedDict, List

from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from core.llm import get_llm, get_embeddings
from core.database import SessionLocal, KnowledgeItem, init_db

from dotenv import load_dotenv


load_dotenv()

# We limit search to these domains to ensure "Trusted" HK content
SAFE_DOMAINS = [
    "hkma.gov.hk", 
    "ifec.org.hk",
    "mpfa.org.hk",
    "ctflife.com.hk"
]

class ResearchState(TypedDict):
    topic: str                  # e.g. MPF in Hong Kong""
    raw_content: str            # Data found from Search
    extracted_facts: List[dict] # Cleaned JSON data
    logs: list                  # List of logs

def search_node(state: ResearchState) -> ResearchState:
    """Uses Tavily to find information on trusted domains. Return combined raw content."""
    print(f"--- SEARCHING: {state['topic']} ---")
    
    tavily = TavilySearch(
        max_results=3,
        include_domains=SAFE_DOMAINS
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

if __name__ == "__main__":
    # Initialize the Database (Create tables if missing)
    print("Initializing Database...")
    init_db()
    
    # Define topics you want to learn about
    topics_to_learn = [
        "Basic infomation of insurance in Hong Kong",
    ]
        # "MPF mandatory contribution rules Hong Kong"
        # "Hong Kong Deposit Protection Scheme limit",
        # "Average inflation rate Hong Kong 2024",
        # "Compound interest definition",
        # "Hong Kong Stock Exchange basic trading rules"

    # Run the Agent for each topic
    for topic in topics_to_learn:
        print(f"\n\n>>> PROCESSING TOPIC: {topic}")
        initial_state = {"topic": topic, "logs": []}
        research_app.invoke(initial_state)

    # Verify Data
    print("\n\n>>> VERIFICATION: Reading from DB...")
    session = SessionLocal()
    items = session.query(KnowledgeItem).all()
    for item in items:
        print(f"[{item.topic}] {item.fact_text[:50]}... (Source: {item.source_url})")
    session.close()