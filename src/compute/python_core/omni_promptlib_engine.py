# Omni PromptLib Template Engine
# Ref: jmpaz/promptlib & dottxt-ai/prompts
from typing import List, Dict
import hashlib
def render_prompt(template: str, variables: Dict) -> str:
    result = template
    for k, v in variables.items(): result = result.replace(f"{{{k}}}", str(v))
    return result
def version_hash(template: str) -> str:
    return hashlib.md5(template.encode()).hexdigest()[:12]
def build_few_shot(examples: List[Dict], query: str, n_shot: int = 3) -> str:
    shots = examples[:n_shot]
    parts = [f"Input: {s.get('input','')}\nOutput: {s.get('output','')}" for s in shots]
    return "\n\n".join(parts) + f"\n\nInput: {query}\nOutput:"
def evaluate_prompt(outputs: List[str], references: List[str]) -> Dict:
    exact = sum(1 for o,r in zip(outputs,references) if o.strip()==r.strip())
    return {"exact_match": round(exact/max(len(references),1),4), "n": len(references)}
