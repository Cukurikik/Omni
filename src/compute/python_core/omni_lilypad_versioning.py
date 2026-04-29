# Omni Lilypad Prompt Versioning Engine
# Ref: Mirascope/lilypad — Prompt versioning, tracing, annotation
from typing import List, Dict
import hashlib

def version_prompt(template: str, variables: Dict) -> Dict:
    content = template + str(sorted(variables.items()))
    hash_val = hashlib.md5(content.encode()).hexdigest()[:12]
    return {"version": hash_val, "template": template, "variables": variables}

def trace_execution(version: str, input_data: Dict, output: str, latency_ms: float) -> Dict:
    return {"version": version, "input": input_data, "output": output,
            "latency_ms": round(latency_ms, 2), "token_count": len(output.split())}

def annotate_trace(trace: Dict, label: str, score: float, notes: str = "") -> Dict:
    trace["annotation"] = {"label": label, "score": round(score, 4), "notes": notes}
    return trace

def compare_versions(traces_v1: List[Dict], traces_v2: List[Dict]) -> Dict:
    avg_lat_v1 = sum(t.get("latency_ms", 0) for t in traces_v1) / max(len(traces_v1), 1)
    avg_lat_v2 = sum(t.get("latency_ms", 0) for t in traces_v2) / max(len(traces_v2), 1)
    avg_score_v1 = sum(t.get("annotation", {}).get("score", 0) for t in traces_v1) / max(len(traces_v1), 1)
    avg_score_v2 = sum(t.get("annotation", {}).get("score", 0) for t in traces_v2) / max(len(traces_v2), 1)
    return {"v1_latency": round(avg_lat_v1, 2), "v2_latency": round(avg_lat_v2, 2),
            "v1_score": round(avg_score_v1, 4), "v2_score": round(avg_score_v2, 4),
            "winner": "v1" if avg_score_v1 > avg_score_v2 else "v2"}
