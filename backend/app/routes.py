# backend/app/routes.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.prompt_engine import optimize_prompt

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str
    goal: str

@router.post("/optimize")
async def optimize(request: PromptRequest):
    optimized = await optimize_prompt(request.prompt, request.goal)
    return {"optimized_prompt": optimized}
