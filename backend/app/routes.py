from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.prompt_engine import optimize_prompt

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str
    goal: str

@router.post("/optimize")
async def optimize(request: PromptRequest):
    try:
        optimized = await optimize_prompt(request.prompt, request.goal)
        return {"optimized_prompt": optimized}
    except HTTPException as e:
        return {"optimized_prompt": f"Error: {e.detail}"}
