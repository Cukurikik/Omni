# Omni OpenGPT Timeline Engine (Python)
# Ref: SunLemuria/OpenGPTAndBeyond
from typing import List, Dict

TIMELINE = [
    {"year": 2018, "model": "GPT-1", "params": "117M", "innovation": "Unsupervised pretraining"},
    {"year": 2019, "model": "GPT-2", "params": "1.5B", "innovation": "Zero-shot generalization"},
    {"year": 2020, "model": "GPT-3", "params": "175B", "innovation": "In-context learning"},
    {"year": 2022, "model": "ChatGPT", "params": "175B+", "innovation": "RLHF alignment"},
    {"year": 2023, "model": "GPT-4", "params": "~1.8T", "innovation": "Multimodal reasoning"},
    {"year": 2024, "model": "GPT-4o", "params": "~1.8T", "innovation": "Omni-modal native"},
]

def get_timeline(after_year: int = 0) -> List[Dict]:
    return [m for m in TIMELINE if m["year"] >= after_year]

def scaling_law_estimate(params_b: float) -> float:
    return round(10.4 * params_b ** (-0.076), 4)
