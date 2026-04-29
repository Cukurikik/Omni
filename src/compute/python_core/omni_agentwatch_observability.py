# Omni AgentWatch Observability Engine
# Ref: cyberark/agentwatch — Apache-2.0
import time
from typing import Dict, List

def trace_event(agent_id: str, action: str, latency_ms: float, tokens: int) -> Dict:
    return {"agent_id": agent_id, "action": action, "latency_ms": round(latency_ms, 2),
            "tokens": tokens, "timestamp": time.time()}

def compute_metrics(events: List[Dict]) -> Dict:
    if not events: return {"count": 0}
    lats = [e["latency_ms"] for e in events]
    toks = [e["tokens"] for e in events]
    return {"count": len(events), "avg_latency": round(sum(lats)/len(lats), 2),
            "p95_latency": round(sorted(lats)[int(len(lats)*0.95)], 2),
            "total_tokens": sum(toks)}

def detect_anomaly(latency: float, threshold: float = 5000.0) -> bool:
    return latency > threshold
