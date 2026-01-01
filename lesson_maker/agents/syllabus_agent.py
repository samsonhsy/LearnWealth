from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from backend.core.llm import get_llm

class SectionDraft(BaseModel):
    title: str = Field(description="Title of the lesson section")
    description: str = Field(description="Short description of what will be covered")
    search_query: str = Field(description="The best search query to find facts for this section")

class CourseDraft(BaseModel):
    course_title: str = Field(description="Catchy title for the course")
    course_description: str = Field(description="Overview/description of the course")
    sections: List[SectionDraft] = Field(description="List of 5-8 distinct sections")

def generate_syllabus(topic: str) -> dict:
    """
    Uses LLM to brainstorm a course structure.
    """
    llm = get_llm(temperature=0.7)
    
    # Force the LLM to return the Pydantic structure
    structured_llm = llm.with_structured_output(CourseDraft)
    
    prompt = f"""
    You are an expert Financial Curriculum Designer for Hong Kong teenagers.
    Create a short, engaging course outline about: '{topic}'.
    
    Requirements:
    - Target Audience: 15-18 year olds (Beginners without business and financial background).
    - Context: Hong Kong specific (mention HK rules if applicable).
    - Structure: 3 to 5 bite-sized sections.
    - Search Query: Create a specific search query for each section so our researcher bot can find data later.
    """
    
    result = structured_llm.invoke(prompt)
    return result.model_dump()