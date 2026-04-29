# Omni Langforge Deployment Engine
# Ref: mme/langforge
from typing import List, Dict
import hashlib

def generate_deployment_manifest(app_name: str, chain_steps: List[Dict]) -> Dict:
    manifest_id = hashlib.sha256(f"{app_name}:{len(chain_steps)}".encode()).hexdigest()[:12]
    
    validated_steps = []
    for step in chain_steps:
        if "type" in step and "config" in step:
            validated_steps.append({
                "id": hashlib.md5(str(step).encode()).hexdigest()[:8],
                "type": step["type"],
                "config_hash": hashlib.md5(str(step["config"]).encode()).hexdigest()[:8],
                "status": "ready"
            })
            
    return {
        "manifest_id": manifest_id,
        "app_name": app_name,
        "deployment_target": "omni-cloud",
        "steps_count": len(validated_steps),
        "steps": validated_steps,
        "version": "1.0.0"
    }

def estimate_chain_latency(chain_steps: List[Dict]) -> float:
    base_latency_ms = 0.0
    for step in chain_steps:
        if step.get("type") == "llm":
            base_latency_ms += 1200.0
        elif step.get("type") == "tool":
            base_latency_ms += 400.0
        else:
            base_latency_ms += 50.0
    return round(base_latency_ms, 2)
