# OMNI Compute Layer - SensorLLM Align
class SensorError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def align_sensor_data(sensor_timeseries: list, llm_embeddings: list) -> Result:
    """Aligns motion sensor timeseries data with LLM semantic embeddings."""
    try:
        if len(sensor_timeseries) != len(llm_embeddings):
            return Result(error=SensorError("Mismatch between sensor windows and text embeddings"))
            
        aligned_pairs = []
        for i in range(len(sensor_timeseries)):
            aligned_pairs.append({
                "time_index": i,
                "sensor_mean": float(sum(sensor_timeseries[i]) / len(sensor_timeseries[i])),
                "semantic_vector": llm_embeddings[i]
            })
            
        return Result(value={"aligned_data": aligned_pairs, "length": len(aligned_pairs)})
    except Exception as e:
        return Result(error=SensorError(f"Alignment failed: {str(e)}"))
