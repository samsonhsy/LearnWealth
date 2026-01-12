from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import json

from core.llm import get_llm

# --- SCHEMAS ---
class AdaptedQuiz(BaseModel):
    question: str = Field(description="The rewritten question using the metaphor")
    options: List[str] = Field(description="List of options (metaphor-adjusted if needed)")
    correct_answer: str = Field(description="The correct answer")
    explanation: str = Field(description="Explanation linking the metaphor to the financial fact")

class TutorState(TypedDict):
    # Inputs
    master_content: str
    master_quiz: dict # {question: "", correct: "", options: []}
    user_interest: str # e.g. "Biology"
    
    # Outputs
    personalized_content: str
    personalized_quiz: dict

def style_transfer_node(state: TutorState):
    """Rewrites content using a metaphor."""
    print(f"--- [Tutor] Personalizing for {state['user_interest']} ---")
    
    llm = get_llm(temperature=0.7) # Creativity allowed here
    
    prompt = f"""
    You are a Personal Tutor for a student who loves: {state['user_interest']}.
    
    ORIGINAL LESSON:
    {state['master_content']}
    
    TASK:
    Rewrite this lesson to be engaging. Use a specific metaphor from {state['user_interest']} to explain the concept.
    
    RULES:
    1. Keep financial numbers/facts ACCURATE (do not change 5% to 10%).
    2. Use emojis.
    3. Keep it under 200 words.
    """
    
    response = llm.invoke(prompt)
    return {"personalized_content": response.content}

def quiz_adapter_node(state: TutorState):
    """Rewrites the quiz to match the new metaphor."""
    print("--- [Tutor] Adapting Quiz ---")
    
    llm = get_llm(temperature=0)
    structured_llm = llm.with_structured_output(AdaptedQuiz)
    
    prompt = f"""
    We have rewritten a lesson using a "{state['user_interest']}" metaphor.
    Now, rewrite the Original Quiz to fit that metaphor.
    
    ORIGINAL QUESTION: {state['master_quiz']['question_text']}
    ORIGINAL ANSWER: {state['master_quiz']['correct_answer']}
    ORIGINAL OPTIONS: {state['master_quiz']['distractors']}
    
    NEW LESSON CONTEXT:
    {state['personalized_content']}
    
    TASK:
    Create a new question that tests the same concept but uses the language of the new lesson.
    The logic of the correct answer must remain the same.
    """
    
    result = structured_llm.invoke(prompt)
    return {"personalized_quiz": result.model_dump()}

workflow = StateGraph(TutorState)
workflow.add_node("style_transfer", style_transfer_node)
workflow.add_node("adapt_quiz", quiz_adapter_node)

workflow.set_entry_point("style_transfer")
workflow.add_edge("style_transfer", "adapt_quiz")
workflow.add_edge("adapt_quiz", END)

tutor_app = workflow.compile()

def run_tutor_agent(content: str, quiz: dict, interest: str):
    """Wrapper to run the agent"""
    initial_state = {
        "master_content": content,
        "master_quiz": quiz,
        "user_interest": interest
    }
    return tutor_app.invoke(initial_state)