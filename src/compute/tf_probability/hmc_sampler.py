import numpy as np
from typing import Callable, Tuple

# OMNI Python Compute Layer: Hamiltonian Monte Carlo Sampler
# Hardcore matrix implementation of HMC derived from TensorFlow Probability concepts.

class HMCSampler:
    def __init__(self, step_size: float = 0.1, num_leapfrog_steps: int = 10):
        self.step_size = step_size
        self.num_leapfrog_steps = num_leapfrog_steps

    def leapfrog(self, q: np.ndarray, p: np.ndarray, 
                 grad_U: Callable[[np.ndarray], np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Symplectic Leapfrog integration step.
        """
        p_half = p - 0.5 * self.step_size * grad_U(q)
        q_new = q + self.step_size * p_half
        
        for _ in range(self.num_leapfrog_steps - 1):
            p_half = p_half - self.step_size * grad_U(q_new)
            q_new = q_new + self.step_size * p_half
            
        p_new = p_half - 0.5 * self.step_size * grad_U(q_new)
        return q_new, p_new

    def sample(self, current_q: np.ndarray, 
               U: Callable[[np.ndarray], float], 
               grad_U: Callable[[np.ndarray], np.ndarray], 
               num_samples: int) -> np.ndarray:
        """
        Executes HMC to draw samples from the target distribution.
        U: Potential energy function (negative log-likelihood).
        """
        samples = np.zeros((num_samples, len(current_q)))
        q = current_q.copy()
        
        for i in range(num_samples):
            # 1. Sample momentum
            p = np.random.randn(len(q))
            current_p = p.copy()
            
            # 2. Simulate Hamiltonian dynamics
            q_new, p_new = self.leapfrog(q, p, grad_U)
            
            # 3. Metropolis-Hastings acceptance step
            # Hamiltonian H = U(q) + K(p), K(p) = p^T p / 2
            current_U = U(q)
            current_K = 0.5 * np.sum(current_p ** 2)
            
            proposed_U = U(q_new)
            proposed_K = 0.5 * np.sum(p_new ** 2)
            
            # Acceptance probability
            alpha = np.exp(current_U - proposed_U + current_K - proposed_K)
            
            if np.random.rand() < alpha:
                q = q_new # Accept
            
            samples[i, :] = q
            
        return samples

def run_inference() -> np.ndarray:
    # Example Target: Standard Normal N(0, 1) -> U(q) = 0.5 * q^2
    def U(q): return 0.5 * np.sum(q**2)
    def grad_U(q): return q
    
    sampler = HMCSampler(step_size=0.1, num_leapfrog_steps=5)
    init_q = np.array([5.0, -5.0])
    
    return sampler.sample(init_q, U, grad_U, 100)
