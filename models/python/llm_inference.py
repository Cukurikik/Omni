"""
=======================================================================
🧠 OMNI AI — LLM Inference Pipeline (Gemini / PaLM / LaMDA)
=======================================================================
Production-ready Python inference pipeline for OMNI's LLM tier.
Supports Gemini Pro/Ultra/Flash, PaLM 2, and conversational AI.

Usage:
    from llm_inference import OmniLLMPipeline
    
    pipeline = OmniLLMPipeline(project_id="omni-tool-9c48b")
    response = pipeline.generate("What is OMNI Framework?")
"""

import os
import json
import time
import logging
from typing import Optional, List, Dict, Any, Generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OMNI-LLM")

# ── Configuration ──

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "omni-tool-9c48b")
GCP_REGION = os.environ.get("GCP_REGION", "us-central1")

# ── Model Registry ──

MODELS = {
    # Gemini Family
    "gemini-pro":   {"endpoint": "gemini-2.5-pro",   "type": "gemini_api", "cost_per_m": 1.25},
    "gemini-ultra": {"endpoint": "gemini-2.5-pro",   "type": "gemini_api", "cost_per_m": 2.50},
    "gemini-flash": {"endpoint": "gemini-2.5-flash",  "type": "gemini_api", "cost_per_m": 0.15},
    
    # PaLM Family
    "palm-text":    {"endpoint": "text-bison@002",    "type": "vertex_ai", "cost_per_m": 0.50},
    "palm-chat":    {"endpoint": "chat-bison@002",    "type": "vertex_ai", "cost_per_m": 0.50},
    "palm-code":    {"endpoint": "code-bison@002",    "type": "vertex_ai", "cost_per_m": 0.50},
    
    # Gemma Family (Open Weights)
    "gemma-4-27b":  {"endpoint": "gemma-4-27b-it",   "type": "vertex_ai", "cost_per_m": 0.10},
    "gemma-3-12b":  {"endpoint": "gemma-3-12b-it",   "type": "vertex_ai", "cost_per_m": 0.05},
    "code-gemma":   {"endpoint": "codegemma-7b-it",   "type": "vertex_ai", "cost_per_m": 0.03},
}


class OmniLLMPipeline:
    """Unified LLM inference pipeline for OMNI Framework."""
    
    def __init__(
        self,
        project_id: str = GCP_PROJECT_ID,
        region: str = GCP_REGION,
        api_key: str = GEMINI_API_KEY,
        default_model: str = "gemini-flash",
    ):
        self.project_id = project_id
        self.region = region
        self.api_key = api_key
        self.default_model = default_model
        self.conversation_history: List[Dict] = []
        
        logger.info(f"🧠 [OMNI LLM] Pipeline initialized: model={default_model}, project={project_id}")
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        top_p: float = 0.95,
        top_k: int = 40,
    ) -> Dict[str, Any]:
        """Generate text using the specified LLM model."""
        
        model_id = model or self.default_model
        model_config = MODELS.get(model_id)
        
        if not model_config:
            raise ValueError(f"Unknown model: {model_id}. Available: {list(MODELS.keys())}")
        
        start = time.time()
        
        logger.info(f"✨ [LLM] Generate: model={model_id}, prompt={len(prompt)} chars, temp={temperature}")
        
        if model_config["type"] == "gemini_api":
            result = self._invoke_gemini_api(
                model_config["endpoint"], prompt, system_prompt,
                temperature, max_tokens, top_p, top_k
            )
        else:
            result = self._invoke_vertex_ai(
                model_config["endpoint"], prompt, system_prompt,
                temperature, max_tokens
            )
        
        latency = time.time() - start
        result["latency_ms"] = int(latency * 1000)
        result["model_used"] = model_id
        
        logger.info(f"✅ [LLM] Response: {len(result.get('text', ''))} chars in {latency:.2f}s")
        
        return result
    
    def chat(
        self,
        message: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Multi-turn conversation with context management."""
        
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": time.time()
        })
        
        # Build context from history
        context = "\n".join([
            f"{'User' if turn['role'] == 'user' else 'Assistant'}: {turn['content']}"
            for turn in self.conversation_history[-20:]  # Last 20 turns
        ])
        
        result = self.generate(
            prompt=context,
            model=model,
            system_prompt=system_prompt or "You are OMNI Telepathy Engine. Respond helpfully.",
        )
        
        self.conversation_history.append({
            "role": "assistant",
            "content": result.get("text", ""),
            "timestamp": time.time()
        })
        
        result["turn_number"] = len(self.conversation_history) // 2
        return result
    
    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        model: str = "code-gemma",
    ) -> Dict[str, Any]:
        """Generate code using code-specialized models."""
        
        code_prompt = f"Write {language} code for the following requirement:\n{prompt}\n\nCode:"
        return self.generate(prompt=code_prompt, model=model, temperature=0.2)
    
    def reason(self, problem: str) -> Dict[str, Any]:
        """Perform chain-of-thought reasoning with Gemini Pro."""
        
        reasoning_prompt = (
            "Think through this problem step by step.\n\n"
            f"Problem: {problem}\n\n"
            "Solution (step by step):"
        )
        return self.generate(
            prompt=reasoning_prompt,
            model="gemini-pro",
            temperature=0.3,
            max_tokens=8192,
        )
    
    def batch_generate(
        self,
        prompts: List[str],
        model: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Process multiple prompts in batch."""
        
        logger.info(f"📦 [LLM] Batch: {len(prompts)} prompts")
        results = []
        for i, prompt in enumerate(prompts):
            logger.info(f"📦 [LLM] Processing {i+1}/{len(prompts)}")
            result = self.generate(prompt=prompt, model=model)
            results.append(result)
        
        return results
    
    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("💬 [LLM] Conversation reset")
    
    # ── Private Methods ──
    
    def _invoke_gemini_api(
        self, model_endpoint: str, prompt: str,
        system_prompt: Optional[str], temperature: float,
        max_tokens: int, top_p: float, top_k: int,
    ) -> Dict[str, Any]:
        """Call Gemini REST API."""
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(model_endpoint)
            
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=top_p,
                top_k=top_k,
            )
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
            )
            
            return {
                "text": response.text,
                "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                "output_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0),
                "finish_reason": "STOP",
            }
            
        except ImportError:
            logger.warning("google-generativeai not installed, using mock response")
            return {
                "text": f"[OMNI LLM Mock] Response for: {prompt[:100]}...",
                "prompt_tokens": len(prompt) // 4,
                "output_tokens": 100,
                "total_tokens": len(prompt) // 4 + 100,
                "finish_reason": "STOP",
            }
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {"text": "", "error": str(e)}
    
    def _invoke_vertex_ai(
        self, model_endpoint: str, prompt: str,
        system_prompt: Optional[str], temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """Call Vertex AI prediction endpoint."""
        
        try:
            from google.cloud import aiplatform
            from vertexai.language_models import TextGenerationModel
            
            aiplatform.init(project=self.project_id, location=self.region)
            model = TextGenerationModel.from_pretrained(model_endpoint)
            
            response = model.predict(
                prompt,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            return {
                "text": response.text,
                "prompt_tokens": len(prompt) // 4,
                "output_tokens": len(response.text) // 4,
                "finish_reason": "STOP",
            }
            
        except ImportError:
            logger.warning("google-cloud-aiplatform not installed, using mock response")
            return {
                "text": f"[OMNI Vertex Mock] Response for: {prompt[:100]}...",
                "prompt_tokens": len(prompt) // 4,
                "output_tokens": 100,
                "finish_reason": "STOP",
            }
        except Exception as e:
            logger.error(f"Vertex AI error: {e}")
            return {"text": "", "error": str(e)}


# ── Convenience Functions ──

def quick_generate(prompt: str, model: str = "gemini-flash") -> str:
    """One-liner text generation."""
    pipeline = OmniLLMPipeline()
    result = pipeline.generate(prompt, model=model)
    return result.get("text", "")


def quick_code(prompt: str, language: str = "python") -> str:
    """One-liner code generation."""
    pipeline = OmniLLMPipeline()
    result = pipeline.generate_code(prompt, language=language)
    return result.get("text", "")


# ── CLI Entry Point ──

if __name__ == "__main__":
    import sys
    
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is the OMNI Framework?"
    
    pipeline = OmniLLMPipeline()
    result = pipeline.generate(prompt)
    
    print(f"\n{'='*60}")
    print(f"🧠 OMNI LLM Pipeline — {result.get('model_used', 'unknown')}")
    print(f"{'='*60}")
    print(f"Response: {result.get('text', 'No response')}")
    print(f"Tokens: {result.get('total_tokens', 'N/A')} | Latency: {result.get('latency_ms', 'N/A')}ms")
    print(f"{'='*60}")
