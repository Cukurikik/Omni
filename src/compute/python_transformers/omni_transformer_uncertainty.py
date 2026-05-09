"""OMNI Compute — Transformer Uncertainty Estimation"""
import logging
import math
import random
from typing import List, Dict

logger = logging.getLogger("omni.uncertainty")

class TransformerUncertaintyEstimator:
    """
    Evaluates uncertainty estimation methods (MC Dropout, Deep Ensembles)
    for Transformer-based architectures in NLU tasks.
    """
    def __init__(self, num_classes: int = 2):
        self.num_classes = num_classes
        logger.info("Initialized Transformer Uncertainty Estimator")

    def _simulate_forward_pass_with_dropout(self, input_features: List[float], dropout_rate: float) -> List[float]:
        """Simulates a forward pass applying dropout mask."""
        logits = []
        for i in range(self.num_classes):
            # Base logit
            base = sum(input_features) * 0.1 + i
            # Dropout perturbation
            mask = [1.0 if random.random() > dropout_rate else 0.0 for _ in range(len(input_features))]
            perturbed = sum(f * m for f, m in zip(input_features, mask)) * 0.1
            logits.append(base + perturbed)
        return logits

    def mc_dropout_inference(self, input_features: List[float], num_samples: int = 10, dropout_rate: float = 0.1) -> Dict[str, float]:
        """
        Monte Carlo Dropout for epistemic uncertainty estimation.
        Runs multiple forward passes with dropout active during inference.
        """
        all_probs = []
        
        for _ in range(num_samples):
            logits = self._simulate_forward_pass_with_dropout(input_features, dropout_rate)
            # Softmax
            max_l = max(logits)
            exp_l = [math.exp(l - max_l) for l in logits]
            sum_exp = sum(exp_l)
            probs = [e / sum_exp for e in exp_l]
            all_probs.append(probs)
            
        # Calculate mean prediction and predictive entropy
        mean_probs = [sum(p[i] for p in all_probs) / num_samples for i in range(self.num_classes)]
        
        # Entropy: -sum(p * log(p))
        entropy = -sum(p * math.log(p + 1e-10) for p in mean_probs)
        
        # Expected Entropy (Aleatoric uncertainty)
        expected_entropy = 0.0
        for probs in all_probs:
            expected_entropy += -sum(p * math.log(p + 1e-10) for p in probs)
        expected_entropy /= num_samples
        
        # Mutual Information (Epistemic uncertainty)
        mutual_information = entropy - expected_entropy
        
        prediction = mean_probs.index(max(mean_probs))
        
        return {
            "prediction": prediction,
            "confidence": max(mean_probs),
            "predictive_entropy": entropy,
            "epistemic_uncertainty": mutual_information,
            "aleatoric_uncertainty": expected_entropy
        }
