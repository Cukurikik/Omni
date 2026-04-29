import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class RecLMTuner:
    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)

    def format_instruction(self, user_history: list, candidate: str) -> str:
        history_str = " -> ".join(user_history)
        return f"User history: {history_str}. Will the user interact with {candidate}? Answer yes or no."

    def predict(self, instruction: str) -> float:
        inputs = self.tokenizer(instruction, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=10)
        return float('yes' in self.tokenizer.decode(outputs[0]).lower())
