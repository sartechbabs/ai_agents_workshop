import os
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SYSTEM = (
    "You are a helpful agent. Decide when to call tools. "
    "After using tools, produce a concise final answer with clear steps."
)

def get_client() -> OpenAI:
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("Missing LLM_API_KEY. Set it in environment or Secrets.")
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    return OpenAI(api_key=api_key, base_url=base_url)

def call_model(messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], model: str, temperature: float = 0.2):
    client = get_client()
    return client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=temperature,
    )

def continue_with_tool_results(messages: List[Dict[str, Any]], model: str, temperature: float = 0.2):
    client = get_client()
    return client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )

def build_tools():
    # JSON schemas the model sees; actual functions live in tools.py
    return [
        {
            "type": "function",
            "function": {
                "name": "tool_calculate",
                "description": "Do basic arithmetic like '2*(10+5)'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Arithmetic expression"}
                    },
                    "required": ["expression"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "tool_web_search",
                "description": "Search the web and return short bullet summaries with sources.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "What to search for"},
                        "max_results": {"type": "integer", "description": "1-10", "default": 5}
                    },
                    "required": ["query"]
                }
            }
        }
    ]
