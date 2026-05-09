"""
moe_multi_agent_forecast.py — Domain / Financial Modeling
Layer: Domain / Business — MoE Stock Forecasting

Implements a Multi-Agent Stock Forecasting system utilizing MoE. 
Instead of a monolithic model predicting prices, this system assigns different
agents (experts) to analyze different market signals (e.g., Sentiment, Technicals,
Macroeconomics). The MoE router acts as the "Portfolio Manager", weighing the
advice of each expert agent to make a final prediction.
"""
import torch
import torch.nn as nn
from typing import List, Dict

class TechnicalAnalysisExpert(nn.Module):
    """Analyzes price action, moving averages, and volume."""
    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1) # Outputs a price delta or signal
        )
    def forward(self, x): return self.net(x)

class SentimentAnalysisExpert(nn.Module):
    """Analyzes NLP embeddings of news and social media sentiment."""
    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1)
        )
    def forward(self, x): return self.net(x)

class MacroEconomicExpert(nn.Module):
    """Analyzes interest rates, inflation data, and broad indices."""
    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )
    def forward(self, x): return self.net(x)

class PortfolioManagerRouter(nn.Module):
    """Routes the market state to the most relevant experts and weighs their signals."""
    def __init__(self, state_dim: int, num_experts: int):
        super().__init__()
        # The router learns which market conditions favor which type of analysis
        self.gate = nn.Sequential(
            nn.Linear(state_dim, state_dim // 2),
            nn.ReLU(),
            nn.Linear(state_dim // 2, num_experts)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        logits = self.gate(x)
        return torch.softmax(logits, dim=-1)

class MultiAgentForecastMoE(nn.Module):
    """
    Combines the agents via a Mixture-of-Experts architecture for financial forecasting.
    """
    def __init__(self, state_dim: int, hidden_dim: int):
        super().__init__()
        
        self.experts = nn.ModuleList([
            TechnicalAnalysisExpert(state_dim, hidden_dim),
            SentimentAnalysisExpert(state_dim, hidden_dim),
            MacroEconomicExpert(state_dim, hidden_dim)
        ])
        
        self.router = PortfolioManagerRouter(state_dim, len(self.experts))
        
    def forward(self, market_state: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        market_state: (Batch, state_dim) containing concatenated market features.
        """
        # Get portfolio manager weights (B, 3)
        agent_weights = self.router(market_state)
        
        # Get predictions from each agent
        agent_predictions = []
        for expert in self.experts:
            agent_predictions.append(expert(market_state)) # (B, 1)
            
        stacked_preds = torch.cat(agent_predictions, dim=1) # (B, 3)
        
        # Final weighted forecast
        final_forecast = torch.sum(stacked_preds * agent_weights, dim=1, keepdim=True)
        
        return {
            "final_prediction": final_forecast,
            "agent_weights": agent_weights,
            "raw_agent_signals": stacked_preds
        }
