# OMNI MOTHER: LibMoE Metrics Logger

class OmniLibMoEMetrics:
    @staticmethod
    def calculate_expert_utilization(expert_token_counts: list) -> float:
        """Calculate utilization percentage (perfect balance = 100%)"""
        if not expert_token_counts:
            return 0.0
            
        total_tokens = sum(expert_token_counts)
        if total_tokens == 0:
            return 0.0
            
        max_possible = max(expert_token_counts) * len(expert_token_counts)
        return (total_tokens / max_possible) * 100.0
