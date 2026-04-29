import torch
import math
from typing import Tuple, Optional

# OMNI DIFFUSERS: DDIM Scheduler
# Python logic for Denoising Diffusion Implicit Models deterministic sampling step.
# Source: huggingface/diffusers

class DDIMError(Exception):
    pass

class DDIMScheduler:
    def __init__(self, num_train_timesteps: int = 1000, beta_start: float = 0.0001, beta_end: float = 0.02):
        self.num_train_timesteps = num_train_timesteps
        
        # Linear beta schedule
        self.betas = torch.linspace(beta_start, beta_end, num_train_timesteps)
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        
    def set_timesteps(self, num_inference_steps: int):
        """Calculates the specific timesteps to evaluate at."""
        step_ratio = self.num_train_timesteps // num_inference_steps
        timesteps = (torch.arange(0, num_inference_steps) * step_ratio).round().flip(0)
        return timesteps.long()

    def step(
        self,
        model_output: torch.Tensor,
        timestep: int,
        sample: torch.Tensor,
        eta: float = 0.0,
    ) -> Tuple[Optional[torch.Tensor], Optional[DDIMError]]:
        """
        Computes the previous sample x_{t-1} given the model output and current sample x_t.
        """
        try:
            # 1. Get alpha values for current and previous timestep
            alpha_prod_t = self.alphas_cumprod[timestep]
            
            # Previous timestep (assuming uniform spacing for simplicity)
            prev_timestep = timestep - (self.num_train_timesteps // 50) # Example 50 inference steps
            if prev_timestep >= 0:
                alpha_prod_t_prev = self.alphas_cumprod[prev_timestep]
            else:
                alpha_prod_t_prev = torch.tensor(1.0)
                
            beta_prod_t = 1 - alpha_prod_t
            
            # 2. Compute predicted original sample x_0 from epsilon
            # x_0 = (x_t - sqrt(1 - alpha_prod_t) * epsilon) / sqrt(alpha_prod_t)
            pred_original_sample = (sample - beta_prod_t ** 0.5 * model_output) / alpha_prod_t ** 0.5
            
            # 3. Compute deterministic direction pointing to x_t
            dir_xt = (1 - alpha_prod_t_prev - eta ** 2) ** 0.5 * model_output
            
            # 4. Compute previous sample x_{t-1}
            # x_{t-1} = sqrt(alpha_prod_t_prev) * x_0 + direction + noise
            noise = torch.randn_like(sample) * eta
            prev_sample = alpha_prod_t_prev ** 0.5 * pred_original_sample + dir_xt + noise
            
            return prev_sample, None
            
        except Exception as e:
            return None, DDIMError(f"DDIM step failed: {str(e)}")
