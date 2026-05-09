# OMNI Compute & AI Layer
# NLP Uncertainty Zoo Integration
# Implements uncertainty quantification (Epistemic and Aleatoric) based on Kaleidophon/nlp-uncertainty-zoo.

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple

class OmniMonteCarloDropout(nn.Module):
    """
    Wraps an Omni Transformer layer to perform Monte Carlo Dropout for epistemic uncertainty estimation.
    """
    def __init__(self, model: nn.Module, num_samples: int = 10, dropout_p: float = 0.1):
        super().__init__()
        self.model = model
        self.num_samples = num_samples
        self.dropout_p = dropout_p
        
        # Ensure model has dropout injected
        self._enable_dropout_during_inference()

    def _enable_dropout_during_inference(self):
        """Forces dropout layers to be active even in eval mode."""
        for module in self.model.modules():
            if module.__class__.__name__.startswith('Dropout'):
                module.train()

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Returns:
            mean_prediction: [batch_size, num_classes]
            uncertainty_variance: [batch_size, num_classes]
        """
        predictions = []
        
        # Run multiple forward passes
        for _ in range(self.num_samples):
            pred = self.model(x)
            predictions.append(pred)
            
        # Stack predictions: [num_samples, batch_size, num_classes]
        stacked_preds = torch.stack(predictions)
        
        # Mean across samples
        mean_pred = torch.mean(stacked_preds, dim=0)
        
        # Variance (Uncertainty)
        variance = torch.var(stacked_preds, dim=0)
        
        return mean_pred, variance

class OmniEvidentialNetwork(nn.Module):
    """
    Directly predicts Dirichlet distribution parameters for classification uncertainty.
    """
    def __init__(self, feature_extractor: nn.Module, num_classes: int):
        super().__init__()
        self.feature_extractor = feature_extractor
        self.evidence_layer = nn.Linear(feature_extractor.output_dim, num_classes)
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        features = self.feature_extractor(x)
        # Evidence must be > 0
        evidence = F.softplus(self.evidence_layer(features))
        
        # Dirichlet parameters (alpha)
        alpha = evidence + 1.0
        
        # Total strength (S)
        S = torch.sum(alpha, dim=1, keepdim=True)
        
        # Belief masses
        belief = evidence / S
        
        # Uncertainty
        uncertainty = self.num_classes / S
        
        return belief, uncertainty.squeeze(1)
