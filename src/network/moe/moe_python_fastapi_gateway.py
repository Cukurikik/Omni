"""
moe_python_fastapi_gateway.py — Network / API
Layer: Network / Python — FastAPI Inference Gateway

While gRPC handles internal cluster traffic, external web clients (React, Mobile)
communicate via HTTP/REST. This Python module uses FastAPI and Starlette to
provide an async, high-throughput ingestion gateway. It handles request validation,
API key auth, and Server-Sent Events (SSE) for streaming text generation.
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
import asyncio
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="OMNI MoE Inference Gateway")

class InferenceRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.95
    stream: bool = False

print("[FastAPI Gateway] Initialized OMNI MoE HTTP/REST Endpoint.")

# Mock Authentication Dependency
async def verify_api_key(request: Request):
    api_key = request.headers.get("Authorization")
    if not api_key or api_key != "Bearer OMNI-SECRET-KEY":
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

@app.post("/v1/completions")
async def create_completion(req: InferenceRequest, token: str = Depends(verify_api_key)):
    """
    Ingests a prompt and routes it to the MoE backend (mocked here).
    Supports both standard JSON response and Server-Sent Events (SSE) streaming.
    """
    if req.stream:
        return StreamingResponse(
            mock_moe_stream(req.prompt, req.max_tokens), 
            media_type="text/event-stream"
        )
    else:
        # Mock synchronous inference
        await asyncio.sleep(0.5)
        return {
            "id": "cmpl-mock123",
            "choices": [{"text": f"[MoE Result for: {req.prompt[:10]}...]", "finish_reason": "stop"}]
        }

async def mock_moe_stream(prompt: str, max_tokens: int):
    """
    Simulates token-by-token generation from the MoE, yielding SSE formatted chunks.
    """
    words = ["The ", "MoE ", "architecture ", "is ", "highly ", "scalable. "]
    for word in words:
        await asyncio.sleep(0.1) # Simulate compute latency
        yield f"data: {{\"choices\": [{{\"text\": \"{word}\"}}]}}\n\n"
    
    yield "data: [DONE]\n\n"

# To run: uvicorn moe_python_fastapi_gateway:app --host 0.0.0.0 --port 8000
