import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    api_key = os.getenv("MESHAPI_API_KEY")
    if not api_key:
        raise ValueError("MESHAPI_API_KEY environment variable not set")
    
    return ChatOpenAI(
        model="openai/gpt-4",
        api_key=api_key,
        base_url="https://api.meshapi.ai/v1", # Typical for OpenAI drop-in endpoints
    )
