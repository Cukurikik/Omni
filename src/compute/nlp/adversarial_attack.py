import torch
import torch.nn as nn
from typing import List, Dict, Any, Union

class OmniResult:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error
    @classmethod
    def ok(cls, value: Any): return cls(True, value=value)
    @classmethod
    def err(cls, error: str): return cls(False, error=error)

class AdversarialAttackEngine:
    def __init__(self, model: nn.Module, tokenizer: Any):
        self.model = model
        self.tokenizer = tokenizer
        self.model.eval()

    def generate_fgsm_attack(self, text: str, label: int, epsilon: float = 0.1) -> OmniResult:
        try:
            inputs = self.tokenizer(text, return_tensors="pt")
            input_ids = inputs["input_ids"]
            
            # Require embeddings to compute gradients
            embeddings = self.model.get_input_embeddings()(input_ids)
            embeddings.retain_grad()
            
            outputs = self.model(inputs_embeds=embeddings)
            loss = nn.CrossEntropyLoss()(outputs.logits, torch.tensor([label], device=outputs.logits.device))
            
            self.model.zero_grad()
            loss.backward()
            
            if embeddings.grad is None:
                return OmniResult.err("Model embedding layer does not support gradients")
                
            perturbed_embeddings = embeddings + epsilon * embeddings.grad.sign()
            
            # Forward pass with perturbed embeddings
            adv_outputs = self.model(inputs_embeds=perturbed_embeddings)
            adv_pred = torch.argmax(adv_outputs.logits, dim=-1).item()
            
            return OmniResult.ok({
                "original_label": label,
                "adversarial_prediction": adv_pred,
                "success": adv_pred != label,
                "loss": float(loss.item())
            })
        except Exception as e:
            return OmniResult.err(f"FGSM Attack failed: {e}")
