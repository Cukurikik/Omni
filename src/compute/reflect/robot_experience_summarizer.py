class ReflectSummarizer:
    def __init__(self, llm_client):
        self.llm = llm_client
        
    def summarize_failure(self, telemetry_data: dict, visual_features: list) -> str:
        prompt = f"Robot failed at state {telemetry_data['state']}. Forces: {telemetry_data['forces']}. Explain the failure and correct it."
        # Call LLM logic
        return f"Reflected Analysis: {prompt}"
