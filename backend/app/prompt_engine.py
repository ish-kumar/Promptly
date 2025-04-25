# backend/app/prompt_engine.py
import httpx
import json
from typing import Literal
from fastapi import HTTPException
from app.config import OPENROUTER_API_KEY

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "mistralai/mistral-7b-instruct:free"


GoalType = Literal["clarity", "creativity", "cost", "safety"]

GOAL_INSTRUCTIONS = {
    "clarity": (
        "Improve the prompt by making it more clear, specific, and unambiguous. "
        "Avoid vague language and ensure the intent is easy to understand."
    ),
    "creativity": (
        "Rewrite the prompt to encourage imaginative, open-ended, and original responses. "
        "Use expressive language that invites creative thinking."
    ),
    "cost": (
        "Rewrite the prompt to be as concise and efficient as possible while preserving its core meaning. "
        "Minimize token usage and remove unnecessary words or complexity."
    ),
    "safety": (
        "Rewrite the prompt to reduce the risk of generating unsafe, biased, or harmful content. "
        "Avoid sensitive topics, leading questions, or ambiguous phrasing that could be misinterpreted."
    )
}

async def optimize_prompt(prompt: str, goal: str) -> str:
    if not OPENROUTER_API_KEY:
        return "Error: OpenRouter API key not configured"

    instruction = GOAL_INSTRUCTIONS.get(goal.lower(), "Rewrite the prompt to improve it.")
    
    system_prompt = (
        "You are a prompt optimization assistant. Your job is to rewrite prompts "
        "based on specific goals like clarity, creativity, cost, or safety."
    )

    user_prompt = (
        f"{instruction} Rewrite the following prompt, and respond ONLY with the improved prompt—do not include any explanation or extra text.\n\n"
        f"Original Prompt:\n{prompt}\n\n"
        f"Optimized Prompt:"
    )
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",  # For local development
        "X-Title": "Promptly",
    }

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OPENROUTER_URL, 
                headers=headers, 
                json=payload
            )
            
            # Print debug information
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code != 200:
                return f"API Error: {response.text}"
                
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Debug - Full error: {str(e)}")  # Debug print
        return f"Error optimizing prompt: {str(e)}"
