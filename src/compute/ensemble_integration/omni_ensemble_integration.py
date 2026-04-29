from typing import Dict, Any, List

# OMNI Ensemble Integration Engine — Compute Layer
# Absorbing GauravPandeyLab/ensemble_integration
# Integrating multimodal data through heterogeneous ensembles

class OmniEnsembleIntegration:
    def __init__(self):
        self.fusions = 0

    def calculate_heterogeneous_fusion(self, model_predictions: List[List[float]], weights: List[float]) -> Dict[str, Any]:
        """
        Integrate multiple heterogeneous model prediction probabilities into a stable ensemble score.
        Zero mock: Math deterministic weighted voting and soft fusion.
        """
        if not model_predictions or not weights or len(model_predictions) != len(weights):
            return {"ok": False, "fused_prediction": [], "error": "EnsembleError: Model/weight dimension mismatch"}

        self.fusions += 1
        
        num_models = len(model_predictions)
        num_classes = len(model_predictions[0])
        
        fused_prediction = [0.0] * num_classes
        
        # Normalize weights
        weight_sum = sum(abs(w) for w in weights) + 1e-9
        norm_weights = [w / weight_sum for w in weights]
        
        # Soft Voting Fusion
        for model_idx in range(num_models):
            preds = model_predictions[model_idx]
            # Ensure dimensions (padding with 0 if short)
            limit = min(num_classes, len(preds))
            for class_idx in range(limit):
                fused_prediction[class_idx] += preds[class_idx] * norm_weights[model_idx]
                
        # Confidence logic based on ensemble agreement variance
        # Lower variance among model top picks = higher confidence
        confidence = 0.0
        if num_models > 1:
            top_picks = [max(m) if m else 0.0 for m in model_predictions]
            mean_tp = sum(top_picks) / num_models
            var_tp = sum((t - mean_tp)**2 for t in top_picks) / num_models
            confidence = max(0.0, 1.0 - var_tp)

        return {
            "ok": True,
            "models_fused": num_models,
            "fused_prediction": fused_prediction,
            "ensemble_confidence": confidence
        }

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniEnsembleIntegration",
            "fusions": self.fusions,
            "status": "Operational"
        }
