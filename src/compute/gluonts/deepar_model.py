"""
OMNI Compute Layer: GluonTS DeepAR Estimator
Probabilistic Auto-Regressive Time Series forecasting.
"""
import torch
import torch.nn as nn
from typing import Tuple, List, Optional

Result = Tuple[Optional[torch.Tensor], Optional[Exception]]

class DeepARCell(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_layers: int = 2):
        super().__init__()
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers, batch_first=True)
        # Mu and Sigma outputs for Gaussian likelihood
        self.mu_proj = nn.Linear(hidden_size, 1)
        self.sigma_proj = nn.Softplus()
        self.sigma_linear = nn.Linear(hidden_size, 1)

    def forward(self, x: torch.Tensor, hidden: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        out, hidden = self.lstm(x, hidden)
        mu = self.mu_proj(out)
        sigma = self.sigma_proj(self.sigma_linear(out)) + 1e-6 # prevent zero variance
        return mu, sigma, hidden

class GluonTSDeepAR:
    def __init__(self, context_length: int, prediction_length: int, hidden_size: int = 40):
        self.context_length = context_length
        self.prediction_length = prediction_length
        self.model = DeepARCell(input_size=1, hidden_size=hidden_size)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-3)

    def compute_loss(self, mu: torch.Tensor, sigma: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        distribution = torch.distributions.Normal(mu, sigma)
        nll = -distribution.log_prob(target)
        return nll.mean()

    def train_step(self, batch_context: torch.Tensor, batch_target: torch.Tensor) -> Result:
        try:
            self.optimizer.zero_grad()
            mu, sigma, _ = self.model(batch_context)
            loss = self.compute_loss(mu, sigma, batch_target)
            loss.backward()
            self.optimizer.step()
            return loss.detach(), None
        except Exception as e:
            return None, e

    def forecast(self, context: torch.Tensor, num_samples: int = 100) -> Result:
        try:
            with torch.no_grad():
                mu, sigma, hidden = self.model(context)
                last_mu = mu[:, -1, :]
                last_sigma = sigma[:, -1, :]
                
                # Ancestral sampling for probabilistic forecast
                samples = torch.normal(last_mu.expand(num_samples, -1), last_sigma.expand(num_samples, -1))
                return samples, None
        except Exception as e:
            return None, e
