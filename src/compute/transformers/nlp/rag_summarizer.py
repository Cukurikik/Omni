"""
OMNI Transformer — Retrieval-Augmented Text Summarizer
Combine retrieval with generation for summarization.
"""
import torch
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RetrievalAugmentedSummarizer:
    """RAG-based summarizer: retrieve similar docs then generate summary."""
    def __init__(self, retriever, generator, tokenizer, max_context_len: int = 2048):
        self.retriever = retriever
        self.generator = generator
        self.tokenizer = tokenizer
        self.max_context_len = max_context_len

    def summarize(self, text: str, reference_docs: Optional[List[str]] = None,
                  max_length: int = 256) -> Dict[str, str]:
        # Retrieve similar documents for context
        context = ""
        sources = []
        if reference_docs and self.retriever:
            result = self.retriever.query(text[:500], top_k=3)
            context = result.get("context", "")
            sources = result.get("sources", [])

        prompt = f"Summarize the following text"
        if context:
            prompt += f" considering this additional context:\n{context[:self.max_context_len]}\n\n"
        prompt += f"Text to summarize:\n{text}\n\nSummary:"

        if hasattr(self.generator, "generate"):
            encoded = self.tokenizer.encode(prompt, max_length=self.max_context_len)
            input_ids = torch.tensor([encoded["input_ids"]], device=next(self.generator.parameters()).device)
            output = self.generator.generate(input_ids, max_new_tokens=max_length, temperature=0.3)
            summary = self.tokenizer.decode(output[0, input_ids.size(1):].tolist())
        else:
            summary = prompt  # fallback

        return {"summary": summary, "sources": sources, "prompt_length": len(prompt)}
