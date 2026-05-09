import torch
import torch.nn as nn
from typing import Dict, Any, Optional

class Result:
    def __init__(self, value: Any = None, error: Optional[Exception] = None):
        self.value = value
        self.error = error
        self.is_success = error is None

    @classmethod
    def ok(cls, value: Any) -> 'Result':
        return cls(value=value)

    @classmethod
    def fail(cls, error: Exception) -> 'Result':
        return cls(error=error)

class TemporalFusionTransformerArch(nn.Module):
    """
    Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting.
    Structural skeleton based on aryan-jadon's loss functions evaluation repo.
    """
    def __init__(self, static_vars: int, dynamic_vars: int, hidden_size: int = 64):
        super().__init__()
        # Simplified TFT Architecture
        self.static_encoder = nn.Linear(static_vars, hidden_size)
        self.dynamic_encoder = nn.LSTM(dynamic_vars, hidden_size, batch_first=True)
        
        # Self Attention for temporal relationships
        self.attn = nn.MultiheadAttention(embed_dim=hidden_size, num_heads=4, batch_first=True)
        
        # Output quantiles (e.g., P10, P50, P90)
        self.quantile_proj = nn.Linear(hidden_size, 3) 

    def forward(self, static_x: torch.Tensor, dynamic_x: torch.Tensor) -> torch.Tensor:
        static_context = self.static_encoder(static_x).unsqueeze(1)
        
        lstm_out, _ = self.dynamic_encoder(dynamic_x)
        
        # Add static context to all temporal steps
        combined = lstm_out + static_context
        
        attn_out, _ = self.attn(combined, combined, combined)
        
        quantiles = self.quantile_proj(attn_out)
        return quantiles

class OmniTimeSeriesForecastingEngine:
    """
    OMNI Compute Layer: Time Series Forecasting Engine evaluating multiple regression loss functions.
    """
    def __init__(self, config: Dict[str, Any]):
        self.static_vars = config.get("static_vars", 5)
        self.dynamic_vars = config.get("dynamic_vars", 10)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = TemporalFusionTransformerArch(self.static_vars, self.dynamic_vars).to(self.device)

    def calculate_quantile_loss(self, predictions: torch.Tensor, targets: torch.Tensor, quantiles: list = [0.1, 0.5, 0.9]) -> torch.Tensor:
        """
        Quantile Regression Loss - essential for TFT multi-horizon bounds.
        predictions shape: (B, T, 3)
        targets shape: (B, T, 1)
        """
        losses = []
        for i, q in enumerate(quantiles):
            pred_q = predictions[:, :, i:i+1]
            err = targets - pred_q
            loss = torch.max((q - 1) * err, q * err)
            losses.append(loss)
            
        return torch.stack(losses, dim=-1).mean()

    def execute_forecasting(self, static_data: torch.Tensor, dynamic_data: torch.Tensor) -> Result:
        try:
            static_data = static_data.to(self.device)
            dynamic_data = dynamic_data.to(self.device)
            
            self.model.eval()
            with torch.no_grad():
                quantiles = self.model(static_data, dynamic_data)
                
            return Result.ok(quantiles)
        except Exception as e:
            return Result.fail(e)

def build_timeseries_engine() -> Result:
    config = {"static_vars": 5, "dynamic_vars": 10}
    return Result.ok(OmniTimeSeriesForecastingEngine(config))
