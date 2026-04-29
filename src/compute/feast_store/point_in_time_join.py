class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class FeatureJoiner:
    def __init__(self):
        pass

    def point_in_time_join(self, entity_df: list[dict], feature_df: list[dict], ttl_seconds: int) -> OmniResult:
        if not entity_df or not feature_df:
            return OmniResult(error="Entity and Feature dataframes cannot be empty")

        if ttl_seconds <= 0:
            return OmniResult(error="TTL must be strictly positive")

        # Deterministic AS-OF join logic matching Feast
        # Assuming dicts have 'entity_id', 'timestamp', and feature columns
        
        # Sort feature_df by timestamp for deterministic lookup
        feature_df = sorted(feature_df, key=lambda x: x.get('timestamp', 0))
        
        joined_result = []
        for entity_row in entity_df:
            e_id = entity_row.get('entity_id')
            e_ts = entity_row.get('timestamp', 0)
            
            # Find the most recent feature row strictly before or exactly at e_ts
            best_match = None
            for feat_row in reversed(feature_df):
                if feat_row.get('entity_id') == e_id and feat_row.get('timestamp', 0) <= e_ts:
                    # Check TTL
                    if e_ts - feat_row.get('timestamp', 0) <= ttl_seconds:
                        best_match = feat_row
                    break
                    
            if best_match:
                # Merge dictionaries
                merged = {**entity_row, **best_match}
                joined_result.append(merged)
            else:
                joined_result.append(entity_row) # Left join behavior

        return OmniResult(value=joined_result)
