import httpx
import openai
import os
from typing import Literal
from fastapi import HTTPException
from app.config import OPENROUTER_API_KEY, GROQ_API_KEY

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "mistralai/mistral-7b-instruct:free"
GROQ_MODEL = "llama-3.1-8b-instant"  # You can also use llama3-8b-8192, etc.

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

def build_prompts(prompt: str, goal: str):
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
    return system_prompt, user_prompt

def call_groq(prompt: str, goal: str) -> str | None:
    if not GROQ_API_KEY:
        print("GROQ API key not configured.")
        return None
    try:
        client = openai.OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        system_prompt, user_prompt = build_prompts(prompt, goal)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=300,
            timeout=15
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GROQ error: {e}")
        return None

async def call_openrouter(prompt: str, goal: str) -> str | None:
    if not OPENROUTER_API_KEY:
        print("OpenRouter API key not configured.")
        return None
    system_prompt, user_prompt = build_prompts(prompt, goal)
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",  # For local development
        "X-Title": "Promptly",
    }
    payload = {
        "model": OPENROUTER_MODEL,
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
            print(f"OpenRouter Status Code: {response.status_code}")
            print(f"OpenRouter Response: {response.text}")
            if response.status_code != 200:
                return None
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"OpenRouter error: {e}")
        return None

async def optimize_prompt(prompt: str, goal: str) -> str:
    # Try Groq first
    result = call_groq(prompt, goal)
    if result:
        return result
    # If Groq fails, try OpenRouter
    result = await call_openrouter(prompt, goal)
    if result:
        return result
    # If both fail, return a clear error
    raise HTTPException(status_code=503, detail="All LLM providers failed. Please try again later.")
