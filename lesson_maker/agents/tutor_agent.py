from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import json

from core.database import search_knowledge_base
from core.llm import get_llm

class TutorState(TypedDict):
    user_query: str         # e.g., "What is MPF?"
    user_interest: str      # e.g., "Chinese History"
    retrieved_fact: str     # Data from DB
    tutorial_content: str   # The final explanation
    quiz_json: dict         # The generated question

def retrieve_node(state: TutorState):
    """Finds the best fact from the database."""
    print(f"--- RETRIEVING INFO FOR: {state['user_query']} ---")
    
    results = search_knowledge_base(state['user_query'], limit=1)
    
    if not results:
        fact = "Sorry, I don't have information on that topic in my trusted database."
    else:
        # We assume the top result is the best one
        item = results[0]
        fact = f"Concept: {item.topic}\nFact: {item.fact_text}\nSource: {item.source_url}"
        
    return {"retrieved_fact": fact}

def analogy_node(state: TutorState):
    """The Creative Writer: Rewrites the fact using the interest."""
    print(f"--- GENERATING ANALOGY ({state['user_interest']}) ---")
    
    llm = get_llm(temperature=0.7) # Higher temp for creativity
    
    prompt = f"""
    You are a Financial Tutor for a student who loves {state['user_interest']}.
    
    OBJECTIVE: Explain the following Financial Fact using a metaphor related to {state['user_interest']}.
    
    THE FACT:
    {state['retrieved_fact']}
    
    CONSTRAINTS:
    - Keep it under 150 words.
    - Be encouraging and fun, with emojis.
    - Do not lose the accuracy of the financial rule (e.g. if it says 5%, mention 5%).
    """
    
    response = llm.invoke(prompt)
    return {"tutorial_content": response.content}

def quiz_node(state: TutorState):
    """The Examiner: Creates a quiz based on the specific analogy used."""
    print("--- GENERATING QUIZ ---")
    
    llm = get_llm()
    
    class QuizSchema(BaseModel):
        question: str = Field(description="The question text")
        options: List[str] = Field(description="List of 3 possible answers")
        correct_answer: str = Field(description="The correct answer text")
        explanation: str = Field(description="Why it is correct")

    structured_llm = llm.with_structured_output(QuizSchema)
    
    prompt = f"""
    Based on the following tutorial, create 1 Multiple Choice Question to test understanding.
    
    TUTORIAL TEXT:
    {state['tutorial_content']}
    
    REQUIREMENT:
    - Use the same metaphor (e.g. if they talked about cells, ask about cells).
    - Ensure one answer is clearly correct based on the financial fact.
    """
    
    quiz_result = structured_llm.invoke(prompt)
    
    # Convert to dict for State
    return {"quiz_json": quiz_result.model_dump()}

# BUILD THE GRAPH
workflow = StateGraph(TutorState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("personalize", analogy_node)
workflow.add_node("generate_quiz", quiz_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "personalize")
workflow.add_edge("personalize", "generate_quiz")
workflow.add_edge("generate_quiz", END)

tutor_app = workflow.compile()

if __name__ == "__main__":
    # Ensure your DB has data from Phase 2 first!
    
    def run_demo(user_query, user_interest):
        print(f"\n{'='*40}")
        print(f"USER: {user_interest} | ASKING: {user_query}")
        print(f"{'='*40}")
        
        initial_state = {
            "user_query": user_query,
            "user_interest": user_interest
        }
        
        # Run the Agent
        result = tutor_app.invoke(initial_state)
        
        print("\n>>> 1. RETRIEVED FACT:")
        print(result['retrieved_fact'])
        
        print("\n>>> 2. PERSONALIZED TUTORIAL:")
        print(result['tutorial_content'])
        
        print("\n>>> 3. QUIZ:")
        print(json.dumps(result['quiz_json'], indent=2, ensure_ascii=False))

    # # Scenario A: The Science Student
    # run_demo(
    #     user_query="What is MPF?", 
    #     user_interest="Biology and Evolution"
    # )
    
    # Scenario B: The History Student
    run_demo(
        user_query="Basic infomation of insurance in Hong Kong", 
        user_interest="Chinese Dynasties and War"
    )