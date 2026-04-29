# Omni Langfuse Observability Engine
# Ref: langfuse/langfuse-docs — MIT
from typing import List, Dict
import time
def create_trace(name: str, metadata: Dict = None) -> Dict:
    return {"trace_id": f"tr-{hash(name+str(time.time()))%10**8}", "name": name,
            "metadata": metadata or {}, "spans": [], "start_time": time.time()}
def add_span(trace: Dict, span_name: str, input_data: str, output_data: str, latency_ms: float) -> Dict:
    span = {"name": span_name, "input": input_data[:200], "output": output_data[:200],
            "latency_ms": round(latency_ms, 2), "tokens": len(output_data.split())}
    trace["spans"].append(span); return span
def compute_trace_cost(spans: List[Dict], cost_per_token: float = 0.00001) -> float:
    return round(sum(s.get("tokens",0)*cost_per_token for s in spans), 6)
def eval_score(trace_id: str, name: str, value: float, comment: str = "") -> Dict:
    return {"trace_id": trace_id, "eval_name": name, "score": round(value,4), "comment": comment}
