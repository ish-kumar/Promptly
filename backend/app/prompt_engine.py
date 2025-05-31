import httpx
import openai
import os
from typing import Literal
from fastapi import HTTPException
from app.config import OPENROUTER_API_KEY, GROQ_API_KEY

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "mistralai/mistral-7b-instruct:free"
GROQ_MODEL = "llama3-70b-8192"  

GoalType = Literal["clarity", "creativity", "cost", "safety", "sora", "code"]

GOAL_INSTRUCTIONS = {
    "clarity": (
        "Improve the prompt by making it more clear, specific, and unambiguous. "
        "Avoid vague language and ensure the intent is easy to understand. "
        "For requests involving code generation or technical tasks (e.g., 'write a Python script', 'create a function', 'debug this code'), "
        "aim to transform vague requests into prompts that provide a clearer specification. This often involves detailing or giving examples for:\n"
        "1. **Inputs**: What data does the code operate on? (e.g., function parameters with types, expected format of input files like CSV/JSON, user input examples, sample data structures).\n"
        "2. **Outputs/Return Values**: What should the code produce? (e.g., function return values with types, format of output files, console messages, expected results for given inputs).\n"
        "3. **Core Logic/Functionality**: What are the key steps, algorithms, or calculations involved? (e.g., specific formulas, business rules, data transformations, step-by-step process if complex).\n"
        "4. **Function Definition (if applicable)**: Suggest clarifying the function name, parameters (names, types, defaults), and expected return type.\n"
        "5. **Error Handling**: Should any specific error conditions be handled, and how?\n"
        "6. **Dependencies/Libraries**: Are any specific libraries required or preferred (e.g., pandas, requests)? Is the use of external libraries okay?\n"
        "7. **Context/Purpose**: Briefly, what is the overall goal or problem the code is intended to solve?\n"
        "8. **Constraints**: Are there any performance needs, Python version requirements, or specific coding style guidelines (e.g., PEP 8)?"
    ),
    "creativity": (
        "Rewrite the prompt to encourage imaginative, open-ended, and original responses. "
        "Use expressive language that invites creative thinking."
    ),
    "cost": (
        "Rewrite the prompt to be as concise and efficient as possible while preserving its core meaning. "
        "Use these optimization techniques:\n"
        "1. Remove redundant words and phrases\n"
        "2. Replace long phrases with shorter synonyms\n"
        "3. Use abbreviations where clear\n"
        "4. Remove unnecessary context if not critical\n"
        "5. Combine multiple sentences into one where possible\n"
        "6. Use active voice instead of passive\n"
        "7. Remove filler words and unnecessary adjectives\n"
        "8. Use symbols instead of words where appropriate (e.g., '&' instead of 'and')\n"
        "9. Remove repeated information\n"
        "10. Use contractions where natural\n"
        "Aim for maximum token reduction while keeping the essential meaning intact."
    ),
    "safety": (
        "Rewrite the prompt to reduce the risk of generating unsafe, biased, or harmful content. "
        "Avoid sensitive topics, leading questions, or ambiguous phrasing that could be misinterpreted."
    ),
    "sora": (
        "Transform the prompt into an optimized Sora video generation prompt that accurately reflects the user's original intent and specified style. "
        "Follow these Sora-specific guidelines:\n"
        "1. **Style Preservation**: Critically, if the original prompt specifies a style (e.g., 'realistic screen recording', 'documentary', 'anime-style'), prioritize and preserve this style. Do not change it to 'cinematic' unless 'cinematic' was the original request or no specific style was mentioned.\n"
        "2. Focus on a clear, impactful moment or sequence based on the original prompt\n"
        "3. Emphasize visual storytelling and scene composition that aligns with the original request\n"
        "4. Include specific camera movements (e.g., 'smooth pan', 'slow zoom', 'steady tracking shot') if appropriate for the desired style\n"
        "5. Specify lighting conditions and atmosphere as described or implied in the original prompt\n"
        "6. Add detailed environmental descriptions from the original prompt\n"
        "7. Include character actions and movements as specified\n"
        "8. **Character Detail & Expression**: If characters are central, include specific visual descriptors (e.g., 'a woman with short, dark curly hair and a distinctive blue scarf,' 'a tall man with a weathered face and kind eyes wearing a tweed jacket') to aid visual consistency. Detail their expressions, posture, and subtle actions to convey emotions and intentions visually.\n"
        "9. Specify visual style, defaulting to the original prompt's style if provided (e.g., 'realistic screen recording', 'cinematic', 'documentary', 'anime-style')\n"
        "10. Add timing cues for scene pacing if relevant\n"
        "11. Include color grading preferences from the original prompt or suggest one that fits the described mood\n"
        "12. Specify any special effects or transitions if mentioned or appropriate\n"
        "13. Suggest **negative prompts** if applicable, to clarify what to avoid (e.g., 'avoid text elements', 'no jump cuts', 'not cartoonish').\\n"
        "14. **Aspect Ratio - User-Driven Only**:\n"
        "    a.  **If User Specifies Aspect Ratio**: If the original user prompt explicitly mentions an aspect ratio (e.g., '16:9 aspect ratio', 'assume 1:1', 'make it portrait'), this exact aspect ratio MUST be preserved and included in the optimized prompt.\n"
        "    b.  **If User Does NOT Specify Aspect Ratio**: If the original user prompt makes NO mention of an aspect ratio, the optimized prompt MUST also make NO mention of an aspect ratio. Do not add or assume any aspect ratio in this case.\n"
        "    Your handling of aspect ratio should solely be determined by its presence or absence in the user's original input.\\n"
        "15. Strive for a balance: provide enough detail for clarity and to guide the AI, but also allow room for AI creativity, especially when the original prompt is exploratory. Avoid over-constraining unless hyper-specificity is the goal.\\n"
        "16. **Visual Storytelling Principle ('Show, Don't Tell')**: Translate abstract concepts, emotions, or internal character states from the original prompt into concrete, observable visual elements. For instance, instead of 'the city was prosperous,' describe 'gleaming futuristic skyscrapers, bustling sky-lanes with sleek vehicles, and citizens in vibrant, high-tech attire.'\n"
        "17. **Sensory & Textural Richness**: Where appropriate for the prompt's intent, suggest details that enhance visual and atmospheric richness. This could include material textures (e.g., 'the rough texture of ancient stone walls,' 'the smooth, reflective surface of a calm lake,' 'delicate patterns of frost on a window'), or subtle atmospheric effects (e.g., 'a gentle mist clinging to the forest floor,' 'the shimmer of heat rising from desert sand,' 'the soft glow of bioluminescent flora').\n"
        "18. **Clarity of Core Focus**: While elaborating, ensure the primary subject, action, or theme of the user's original prompt remains the clear focal point of the optimized version. New details should support and enhance this core, not overshadow or contradict it.\n\n"
        "Important Sora-specific considerations:\n"
        "- Ensure smooth transitions between scenes and actions\n"
        "- Maintain consistent physics and lighting throughout the video\n"
        "- Keep camera movements realistic and achievable\n"
        "- Avoid sudden changes in camera angles or lighting\n"
        "- Ensure all elements maintain visual consistency\n"
        "- Focus on achievable camera movements and transitions\n"
        "- Maintain realistic physics and environmental interactions\n"
        "- Avoid rapid camera movements or complex transitions\n"
        "- Keep lighting changes gradual and natural\n"
        "- Ensure consistent scale and proportions\n\n"
        "Content Guidelines:\n"
        "- Keep character movements and interactions natural and continuous\n"
        "- Avoid complex physics or impossible scenarios\n"
        "- Keep character interactions simple and natural\n"
        "- Focus on visual elements rather than complex narratives\n"
        "- Avoid text or writing in the scene\n"
        "- Ensure actions and movements are physically possible\n"
        "- Avoid complex particle effects or simulations\n"
        "- Keep character count and interactions minimal\n"
        "- Avoid complex environmental changes\n\n"
        "Creative Elements:\n"
        "- Use descriptive language for visual details\n"
        "- Include emotional tone and mood\n"
        "- Specify time of day and weather conditions\n"
        "- Add environmental sounds and ambiance\n"
        "- Consider the overall visual aesthetic\n"
        "- Focus on creating a cohesive visual story\n"
        "- Balance detail with feasibility\n"
        "- Use clear, specific descriptions\n"
        "- Maintain consistent visual style\n"
        "- Focus on key visual elements\n\n"
        "Quality Assurance:\n"
        "- Ensure all elements are physically possible\n"
        "- Keep movements and transitions smooth\n"
        "- Maintain consistent lighting and physics\n"
        "- Avoid complex or rapid changes\n"
        "- Focus on achievable visual effects\n\n"
        "Make the prompt detailed and specific while ensuring it's within Sora's capabilities. Focus on creating a visually stunning and technically achievable scene with consistent quality throughout."
    ),
    "code": (
        "Rewrite the prompt to optimize it for code generation. "
        "Make the requirements explicit and actionable for a developer or code-generating AI. "
        "Include, where appropriate:\n"
        "1. Clear function or class definitions, including names, parameters (with types), and return types.\n"
        "2. Example inputs and expected outputs.\n"
        "3. Any required libraries or dependencies.\n"
        "4. Error handling and edge case considerations.\n"
        "5. Coding style or formatting requirements (e.g., PEP 8 for Python).\n"
        "6. Constraints on performance, memory, or compatibility (e.g., Python version).\n"
        "7. If relevant, include docstrings or comments for clarity.\n"
        "8. Avoid unnecessary natural language explanations—focus on actionable code requirements."
    )
}

def build_prompts(prompt: str, goal: str):
    instruction = GOAL_INSTRUCTIONS.get(goal.lower(), "Rewrite the prompt to improve it.")
    system_prompt = (
        "You are an expert prompt optimization assistant. Your task is to rewrite prompts to achieve specific optimization goals. "
        "IMPORTANT: Respond ONLY with the optimized prompt text. Do not include any explanations, introductions, or additional text. "
        "Follow these principles:\n"
        "1. **Crucially, meticulously follow all specific instructions and guidelines provided in the 'Optimization Goal' section of the user's message. This is your primary directive for the transformation.**\n"
        "2. Always preserve the core intent and essential information from the original prompt.\n"
        "3. Apply optimization techniques appropriate for the stated goal and the detailed instructions provided in the 'Optimization Goal' section.\n"
        "4. Ensure the optimized prompt is likely to generate high-quality, relevant responses from the target video AI.\n"
        "5. Remove any unnecessary elements from the original prompt that don't contribute to the goal.\n"
        "6. Maintain natural language flow and readability in the optimized prompt.\n"
        "7. Consider the target model's capabilities and limitations (as outlined in the goal-specific instructions if available).\n"
        "8. Use best practices for prompt engineering for video generation, informed by the detailed goal instructions.\n"
        "9. If the original prompt is already perfectly optimal for the goal, return it unchanged.\n"
        "10. NEVER include phrases like 'here is', 'here's', or any other explanatory text in your response.\n"
        "11. NEVER include markdown formatting or code blocks in your response."
    )
    user_prompt = (
        f"Optimization Goal: {instruction}\n\n"
        f"Original Prompt:\n{prompt}\n\n"
        f"Return ONLY the optimized prompt text, with no additional text or formatting."
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
            max_tokens=1024,
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
        "max_tokens": 1024,
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
