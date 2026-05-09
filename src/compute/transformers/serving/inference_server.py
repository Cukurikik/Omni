"""
OMNI Transformer — Inference Server
FastAPI-based model serving with batching, streaming, health checks.
Learned from: vLLM architecture, Triton concepts
"""
import asyncio
import logging
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


@dataclass
class InferenceConfig:
    max_batch_size: int = 32
    max_seq_len: int = 2048
    max_new_tokens: int = 512
    temperature: float = 0.7
    top_k: int = 50
    top_p: float = 0.9
    timeout_seconds: float = 30.0
    device: str = "cuda"


class RequestQueue:
    """Async request queue for continuous batching."""
    def __init__(self, max_batch_size: int = 32, max_wait_ms: float = 50.0):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms

    async def add(self, request: Dict[str, Any]) -> asyncio.Future:
        future = asyncio.get_event_loop().create_future()
        await self.queue.put((request, future))
        return future

    async def get_batch(self) -> List[tuple]:
        batch = []
        try:
            item = await asyncio.wait_for(self.queue.get(), timeout=self.max_wait_ms / 1000)
            batch.append(item)
        except asyncio.TimeoutError:
            return batch

        while len(batch) < self.max_batch_size:
            try:
                item = self.queue.get_nowait()
                batch.append(item)
            except asyncio.QueueEmpty:
                break
        return batch


class ModelServer:
    """Production model inference server with continuous batching."""
    def __init__(self, model: nn.Module, config: InferenceConfig, tokenizer=None):
        self.model = model
        self.config = config
        self.tokenizer = tokenizer
        self.device = torch.device(config.device if torch.cuda.is_available() else "cpu")
        self.model.to(self.device).eval()
        self.request_queue = RequestQueue(config.max_batch_size)
        self._running = False
        self.stats = {"total_requests": 0, "total_tokens": 0, "avg_latency_ms": 0.0}

    @torch.inference_mode()
    def generate_batch(self, input_ids: torch.Tensor, **kwargs) -> torch.Tensor:
        input_ids = input_ids.to(self.device)
        if hasattr(self.model, "generate"):
            return self.model.generate(
                input_ids, max_new_tokens=kwargs.get("max_new_tokens", self.config.max_new_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                top_k=kwargs.get("top_k", self.config.top_k),
                top_p=kwargs.get("top_p", self.config.top_p),
            )
        # Fallback: single forward pass
        output = self.model(input_ids)
        return output.get("logits", output)

    async def process_request(self, text: str, **kwargs) -> Dict[str, Any]:
        start = time.perf_counter()
        if self.tokenizer:
            encoded = self.tokenizer.encode(text, max_length=self.config.max_seq_len)
            input_ids = torch.tensor([encoded["input_ids"]])
        else:
            input_ids = torch.tensor([[ord(c) % 30000 for c in text[:self.config.max_seq_len]]])

        output = self.generate_batch(input_ids, **kwargs)
        latency = (time.perf_counter() - start) * 1000

        result_text = ""
        if self.tokenizer and hasattr(output, "tolist"):
            result_text = self.tokenizer.decode(output[0].tolist())

        self.stats["total_requests"] += 1
        self.stats["avg_latency_ms"] = (self.stats["avg_latency_ms"] * (self.stats["total_requests"] - 1) + latency) / self.stats["total_requests"]

        return {"generated_text": result_text, "latency_ms": round(latency, 2), "tokens_generated": output.shape[-1] if hasattr(output, "shape") else 0}

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "device": str(self.device),
            "model_loaded": True,
            "stats": self.stats,
            "gpu_memory_mb": round(torch.cuda.memory_allocated() / 1e6, 1) if torch.cuda.is_available() else 0,
        }
