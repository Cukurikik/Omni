# Omni AutoMix LLM Router
# Ref: automix-llm/automix — Apache-2.0
# Implements: Self-verification, meta-verification, POMDP-based routing
import math
from typing import List, Dict, Tuple

def self_verification_score(answer: str, context: str) -> float:
    a_tokens = set(answer.lower().split())
    c_tokens = set(context.lower().split())
    if not a_tokens: return 0.0
    overlap = len(a_tokens & c_tokens)
    return round(overlap / len(a_tokens), 6)

def meta_verify(sv_scores: List[float], threshold: float = 0.6) -> bool:
    if not sv_scores: return False
    mean_sv = sum(sv_scores) / len(sv_scores)
    return mean_sv >= threshold

def pomdp_route_decision(confidence: float, cost_small: float, cost_large: float,
                          quality_gain: float, threshold: float = 0.5) -> str:
    expected_value_upgrade = quality_gain * (1.0 - confidence)
    marginal_cost = cost_large - cost_small
    if marginal_cost <= 0: return "large_model"
    benefit_per_cost = expected_value_upgrade / marginal_cost
    return "large_model" if benefit_per_cost > threshold else "small_model"

def automix_pipeline(query: str, context: str, slm_answer: str,
                     cost_s: float = 0.01, cost_l: float = 0.10) -> Dict:
    sv = self_verification_score(slm_answer, context)
    verified = meta_verify([sv])
    route = "small_model" if verified else pomdp_route_decision(sv, cost_s, cost_l, 0.3)
    return {"query": query[:50], "sv_score": sv, "meta_verified": verified,
            "routed_to": route, "estimated_cost": cost_s if route == "small_model" else cost_l}
