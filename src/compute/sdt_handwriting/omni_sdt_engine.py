from typing import Dict, Any
from dataclasses import dataclass
import numpy as np

# OMNI SDT Engine — Compute Layer
# Absorbing dailenson/SDT (CVPR 2023): Style-Disentangled Transformer for handwriting generation.
# Implements GMM-based stroke prediction: mixture of Gaussians for pen trajectory.

@dataclass
class SdtResult:
    ok: bool
    trajectory: np.ndarray = None
    error: str = None

class OmniSdtEngine:
    def __init__(self, n_mixtures: int = 20, d_model: int = 512):
        self.n_mixtures = n_mixtures
        self.d_model = d_model
        self.generations = 0

    def sample_gmm_stroke(self, gmm_params: np.ndarray, n_steps: int = 100) -> SdtResult:
        """
        Samples pen trajectory from Gaussian Mixture Model parameters.
        gmm_params: (n_mixtures, 6) — [pi, mu_x, mu_y, sigma_x, sigma_y, rho] per component
        """
        if gmm_params.ndim != 2 or gmm_params.shape[0] != self.n_mixtures or gmm_params.shape[1] != 6:
            return SdtResult(False, error=f"SDTError: Expected ({self.n_mixtures}, 6)")
        try:
            self.generations += 1
            pis = gmm_params[:, 0]
            # Softmax for mixture weights
            exp_pi = np.exp(pis - np.max(pis))
            weights = exp_pi / np.sum(exp_pi)

            trajectory = np.zeros((n_steps, 2), dtype=np.float64)
            for t in range(n_steps):
                # Select mixture component
                k = np.random.choice(self.n_mixtures, p=weights)
                mu_x, mu_y = gmm_params[k, 1], gmm_params[k, 2]
                sigma_x = max(abs(gmm_params[k, 3]), 1e-4)
                sigma_y = max(abs(gmm_params[k, 4]), 1e-4)
                rho = np.clip(gmm_params[k, 5], -0.99, 0.99)

                # Sample from bivariate Gaussian
                cov = [[sigma_x**2, rho*sigma_x*sigma_y],
                       [rho*sigma_x*sigma_y, sigma_y**2]]
                dx, dy = np.random.multivariate_normal([mu_x, mu_y], cov)
                if t == 0:
                    trajectory[t] = [dx, dy]
                else:
                    trajectory[t] = trajectory[t-1] + [dx, dy]

            return SdtResult(True, trajectory=trajectory.astype(np.float32))
        except Exception as e:
            return SdtResult(False, error=f"SDTError: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniSdtEngine", "generations": self.generations,
                "n_mixtures": self.n_mixtures, "status": "Operational"}
