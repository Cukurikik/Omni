from typing import Dict, Any

class OmniAgentWatchMonitor:
    """OMNI Compute Layer: AgentWatch AI Observability"""
    
    def __init__(self, sampling_rate: float = 1.0):
        self.sampling_rate = sampling_rate

    def log_interaction(self, agent_id: str, payload_size: int, duration_ms: float) -> Dict[str, Any]:
        if payload_size <= 0:
            return {"status": "dropped"}
            
        # Deterministic telemetry logging
        throughput = payload_size / (duration_ms / 1000.0) if duration_ms > 0 else 0
        
        return {
            "agent_id": agent_id,
            "throughput_bps": float(throughput),
            "latency_ms": float(duration_ms),
            "sampled": True
        }
