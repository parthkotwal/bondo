import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment.")
        
        _client = OpenAI(api_key=api_key)
    
    return _client

def call_llm(messages, model="gpt-4.1-mini", response_format=None):
    """
    Generic OpenAI chat completion call.
    """
    client = get_client()

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format=response_format,
        temperature=0.2,
    )
    return resp.choices[0].message.content