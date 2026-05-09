"""OMNI Compute — Continual Prompt Tuning (CPT) for Few-Shot Learning"""
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("omni.cpt")

class CPTContinualLearner:
    """
    Continual Training of Language Models for Few-Shot Learning.
    Mitigates catastrophic forgetting using soft-prompt tuning and replay.
    """
    def __init__(self, prompt_length: int = 10, embedding_dim: int = 768):
        self.prompt_length = prompt_length
        self.embedding_dim = embedding_dim
        # Global shared prompt
        self.global_prompt = [[0.01 * i for i in range(embedding_dim)] for _ in range(prompt_length)]
        # Task-specific prompts
        self.task_prompts: Dict[str, List[List[float]]] = {}
        # Memory buffer for replay (Few-Shot samples)
        self.memory_buffer: Dict[str, List[str]] = {}
        logger.info(f"Initialized CPT Few-Shot Learner (prompt_len={prompt_length})")

    def register_task(self, task_name: str, few_shot_examples: List[str]):
        """Initializes a new task prompt and stores few-shot examples for replay."""
        if task_name not in self.task_prompts:
            # Initialize with small random noise
            import random
            self.task_prompts[task_name] = [[random.uniform(-0.01, 0.01) for _ in range(self.embedding_dim)] for _ in range(self.prompt_length)]
        
        self.memory_buffer[task_name] = few_shot_examples[:10] # Store max 10 for replay

    def _simulate_prompt_gradient(self, prompt: List[List[float]], target: str) -> List[List[float]]:
        """Simulates gradients to update the soft prompt."""
        return [[p * 0.99 for p in row] for row in prompt] # Decay for simulation

    def train_task(self, task_name: str, epochs: int = 3):
        """Continual learning loop."""
        if task_name not in self.task_prompts:
            raise ValueError(f"Task {task_name} not registered")
            
        logger.info(f"Training CPT on task: {task_name}")
        for epoch in range(epochs):
            # 1. Train on current task
            current_prompt = self.task_prompts[task_name]
            self.task_prompts[task_name] = self._simulate_prompt_gradient(current_prompt, "target")
            
            # 2. Replay memory from past tasks to prevent catastrophic forgetting
            for past_task, examples in self.memory_buffer.items():
                if past_task != task_name:
                    # Update global prompt slightly using past task data
                    self.global_prompt = self._simulate_prompt_gradient(self.global_prompt, "replay")

    def predict(self, task_name: str, input_text: str) -> List[float]:
        """Inference using global + task-specific prompt concatenation."""
        if task_name not in self.task_prompts:
            return [0.0]
            
        # Concatenate global and task prompts
        combined_prompt = self.global_prompt + self.task_prompts[task_name]
        
        # Simulate LLM forward pass with prepended soft prompts
        score = sum(sum(row) for row in combined_prompt) * len(input_text)
        # Return probability distribution (simulated)
        import math
        prob = 1.0 / (1.0 + math.exp(-score * 0.001))
        return [prob, 1.0 - prob]
