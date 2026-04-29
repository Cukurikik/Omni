# Omni Flacuna Instruction Mixer
# Ref: declare-lab/flacuna
from typing import List, Dict

def mix_instruction_sets(flan: List[Dict], vicuna: List[Dict], ratio: float = 0.7) -> List[Dict]:
    n_flan = int(len(flan) * ratio)
    n_vic = len(vicuna) - n_flan if n_flan < len(vicuna) else len(vicuna)
    return flan[:n_flan] + vicuna[:n_vic]

def format_instruction(instruction: str, input_text: str, output: str) -> Dict:
    return {"prompt": f"### Instruction:\n{instruction}\n### Input:\n{input_text}\n### Response:",
            "completion": output}

def compute_instruction_diversity(instructions: List[str]) -> float:
    unique_starts = set(inst.split()[:3] if inst else () for inst in instructions)
    return round(len(unique_starts) / max(len(instructions), 1), 6)
