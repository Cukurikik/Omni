# OMNI Compute Layer - AIGC Aggregator
class AIGCError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def aggregate_research(data_sources: list) -> Result:
    """Aggregates and deduplicates AIGC research groups and publications."""
    try:
        if not data_sources:
            return Result(error=AIGCError("No data sources provided"))
            
        unique_groups = {}
        for src in data_sources:
            group_name = src.get("group_name")
            if group_name and group_name not in unique_groups:
                unique_groups[group_name] = src
                
        return Result(value={"total_groups": len(unique_groups), "groups": list(unique_groups.values())})
    except Exception as e:
        return Result(error=AIGCError(f"Aggregation failed: {str(e)}"))
