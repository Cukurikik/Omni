from typing import Dict

class OmniDSBenchEvaluator:
    """OMNI Compute Layer: DSBench Data Science Agent Evaluator"""
    
    def __init__(self):
        self.metrics = ["data_cleaning", "modeling", "evaluation"]

    def score_agent(self, agent_logs: str) -> Dict[str, float]:
        if not agent_logs:
            return {m: 0.0 for m in self.metrics}
            
        logs_lower = agent_logs.lower()
        return {
            "data_cleaning": 1.0 if "dropna" in logs_lower or "impute" in logs_lower else 0.0,
            "modeling": 1.0 if "fit" in logs_lower or "train" in logs_lower else 0.0,
            "evaluation": 1.0 if "accuracy" in logs_lower or "f1" in logs_lower else 0.0
        }
