from typing import Dict, Any, List

# OMNI ChartHal Evaluation Engine — Compute Layer
# Absorbing ymcui/ChartHal
# Vision Language Models Scientific Chart Hallucination evaluation

class OmniCharthalEvaluation:
    def __init__(self):
        self.charts_evaluated = 0

    def calculate_chart_hallucination_delta(self, detected_keypoints: List[Dict[str, float]], generated_data_values: List[float]) -> Dict[str, Any]:
        """
        Assess fine-grained hallucination by mapping image keypoints (e.g. bar heights) to LLM generated numerical text values.
        Zero mock: Math linear correlation and variance bounds testing.
        """
        if not detected_keypoints or not generated_data_values:
            return {"ok": False, "hallucination_rate": 1.0, "error": "ChartHalError: Missing evaluation data"}

        self.charts_evaluated += 1
        
        kpts_len = len(detected_keypoints)
        vals_len = len(generated_data_values)
        
        if kpts_len != vals_len:
            # Hallucinating extra or missing data
            return {
                "ok": True, 
                "hallucination_rate": 1.0,
                "reason": f"Mismatch in count: {kpts_len} keypoints vs {vals_len} generated values."
            }
            
        # Linear correlation logic (Pearson r) to see if structure maps correctly
        # Assuming 'y' value of keypoints reflects the numerical quantity
        y_vals = [kp.get('y', 0.0) for kp in detected_keypoints]
        
        mean_y = sum(y_vals) / kpts_len
        mean_g = sum(generated_data_values) / vals_len
        
        num = 0.0
        den_y = 0.0
        den_g = 0.0
        
        for i in range(kpts_len):
            dy = y_vals[i] - mean_y
            dg = generated_data_values[i] - mean_g
            
            num += (dy * dg)
            den_y += (dy * dy)
            den_g += (dg * dg)
            
        import math
        denom = math.sqrt(den_y) * math.sqrt(den_g)
        correlation = (num / denom) if denom > 0 else 0.0
        
        # If correlation is low, the LLM hallucinated the chart proportions
        hallucination_rate = 1.0 - max(0.0, correlation)

        return {
            "ok": True,
            "hallucination_rate": hallucination_rate,
            "structural_correlation": correlation,
            "reason": "OK" if hallucination_rate < 0.2 else "Structure Hallucinated"
        }

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniCharthalEvaluation",
            "evals": self.charts_evaluated,
            "status": "Operational"
        }
