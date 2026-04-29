import numpy as np
from typing import Tuple, Optional

# OMNI GENERATIVE-MODELS: DDPM Reverse Diffusion Step
# Mathematical implementation of the Denoising Diffusion Probabilistic Models backward pass.
# Source: Stability-AI/generative-models

class DiffusionError(Exception):
    pass

class DDPMNoiseScheduler:
    def __init__(self, num_timesteps: int = 1000, beta_start: float = 1e-4, beta_end: float = 0.02):
        self.num_timesteps = num_timesteps
        
        # Linear beta schedule
        self.betas = np.linspace(beta_start, beta_end, num_timesteps)
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = np.cumprod(self.alphas)
        
        # Pre-calculate terms for the reverse step calculation
        self.sqrt_recip_alphas = np.sqrt(1.0 / self.alphas)
        self.sqrt_alphas_cumprod = np.sqrt(self.alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = np.sqrt(1.0 - self.alphas_cumprod)
        
        self.posterior_variance = self.betas * (1.0 - np.append([1.0], self.alphas_cumprod[:-1])) / (1.0 - self.alphas_cumprod)

    def reverse_step(
        self, 
        model_output_noise: np.ndarray, 
        timestep: int, 
        sample: np.ndarray
    ) -> Tuple[Optional[np.ndarray], Optional[DiffusionError]]:
        """
        Calculates x_{t-1} given x_t and the noise predicted by the U-Net.
        
        Args:
            model_output_noise: epsilon_theta(x_t, t)
            timestep: t
            sample: x_t
        """
        try:
            if timestep < 0 or timestep >= self.num_timesteps:
                return None, DiffusionError(f"Timestep {timestep} out of bounds.")
                
            if model_output_noise.shape != sample.shape:
                return None, DiffusionError("Shape mismatch between model output and sample.")

            t = timestep
            
            # Equation: x_{t-1} = 1/sqrt(alpha_t) * (x_t - (beta_t / sqrt(1 - alpha_bar_t)) * epsilon_theta) + sigma_t * z
            
            beta_t = self.betas[t]
            sqrt_one_minus_alpha_bar_t = self.sqrt_one_minus_alphas_cumprod[t]
            sqrt_recip_alpha_t = self.sqrt_recip_alphas[t]
            
            # Predict the mean
            pred_mean = sqrt_recip_alpha_t * (sample - (beta_t / sqrt_one_minus_alpha_bar_t) * model_output_noise)
            
            if t == 0:
                # No noise added at the last step
                return pred_mean, None
            else:
                # Add posterior variance noise
                noise = np.random.randn(*sample.shape)
                sigma_t = np.sqrt(self.posterior_variance[t])
                
                x_prev = pred_mean + sigma_t * noise
                return x_prev, None

        except Exception as e:
            return None, DiffusionError(f"Reverse diffusion step failed: {str(e)}")
