import os
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings

from dotenv import load_dotenv

load_dotenv()

def get_llm(temperature=0, model_name="gpt-4o-mini"):
    # github models    
    llm = ChatOpenAI(
        model=model_name,
        api_key=os.getenv("GITHUB_TOKEN"),      
        base_url=os.getenv("OPENAI_BASE_URL"), 
        temperature=temperature
    )
    return llm

def get_embeddings(model_name="all-MiniLM-L6-v2"):
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    return embeddings