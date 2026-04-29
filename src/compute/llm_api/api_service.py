from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Omni LLM API StarterKit")

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 100

@app.post("/api/v1/generate")
async def generate_text(req: GenerateRequest):
    if not req.prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    # Production generator hook
    return {"text": f"Generated response for: {req.prompt[:10]}..."}
