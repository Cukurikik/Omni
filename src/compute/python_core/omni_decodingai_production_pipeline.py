# Omni DecodingAI Production Pipeline (Python)
# Compute: Production-grade ML pipeline patterns.
# Ref: decodingai-magazine/articles-code
import hashlib, json
from typing import Dict, List

def create_pipeline_manifest(steps: List[str], version: str) -> Dict:
    fingerprint = hashlib.sha256(json.dumps(steps).encode()).hexdigest()[:16]
    return {"steps": steps, "version": version, "fingerprint": fingerprint, "n_steps": len(steps)}

def validate_pipeline(manifest: Dict) -> Dict:
    if not manifest.get("steps"):
        return {"valid": False, "error": "OMNI_ERR: No steps defined"}
    if not manifest.get("version"):
        return {"valid": False, "error": "OMNI_ERR: No version"}
    return {"valid": True, "fingerprint": manifest.get("fingerprint", "")}
