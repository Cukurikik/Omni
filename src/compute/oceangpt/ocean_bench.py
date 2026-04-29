import json

class OceanBenchEvaluator:
    def __init__(self, benchmark_file: str):
        self.benchmark_file = benchmark_file
        
    def evaluate(self, model_responses: dict) -> dict:
        # Load gold standard
        with open(self.benchmark_file, 'r') as f:
            gold = json.load(f)
            
        correct = 0
        total = len(gold)
        for key, ans in gold.items():
            if key in model_responses and model_responses[key].strip() == ans.strip():
                correct += 1
                
        return {"accuracy": correct / total if total > 0 else 0.0}
