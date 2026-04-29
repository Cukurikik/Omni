import torch
import torch.nn as nn
from typing import Tuple
from omni_core.result import OmniResult, Ok, Err

class AdversarialAttackGenerator:
    """
    OMNI COMPUTE LAYER: Adversarial Robustness
    Implements PGD (Projected Gradient Descent) math for fooling neural networks.
    Zero-Mock: Uses pure PyTorch tensor math.
    """
    def __init__(self, model: nn.Module, epsilon: float = 0.03, alpha: float = 0.01, iters: int = 40):
        self.model = model
        self.epsilon = epsilon
        self.alpha = alpha
        self.iters = iters

    def generate_pgd(self, image: torch.Tensor, label: torch.Tensor) -> OmniResult[torch.Tensor, str]:
        try:
            perturbed_image = image.clone().detach().requires_grad_(True)
            loss_fn = nn.CrossEntropyLoss()

            for _ in range(self.iters):
                outputs = self.model(perturbed_image)
                loss = loss_fn(outputs, label)
                
                self.model.zero_grad()
                loss.backward()
                
                with torch.no_grad():
                    # PGD step
                    adv_image = perturbed_image + self.alpha * perturbed_image.grad.sign()
                    # Projection
                    eta = torch.clamp(adv_image - image, min=-self.epsilon, max=self.epsilon)
                    perturbed_image = torch.clamp(image + eta, min=0, max=1).requires_grad_(True)
            
            return Ok(perturbed_image.detach())
        except Exception as e:
            return Err(f"PGD generation failed: {str(e)}")
