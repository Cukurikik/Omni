# Omni Lion Adversarial Distillation Engine
# Ref: YJiangcm/Lion — EMNLP 2023, MIT
# Implements: 3-stage adversarial distillation loop
from typing import List, Dict

def imitation_loss(student_logits: List[float], teacher_logits: List[float]) -> float:
    import math
    def kl_div(p, q):
        return sum(pi * math.log(max(pi, 1e-9) / max(qi, 1e-9)) for pi, qi in zip(p, q) if pi > 0)
    s_sum = sum(math.exp(s) for s in student_logits) or 1
    t_sum = sum(math.exp(t) for t in teacher_logits) or 1
    s_prob = [math.exp(s) / s_sum for s in student_logits]
    t_prob = [math.exp(t) / t_sum for t in teacher_logits]
    return round(kl_div(t_prob, s_prob), 6)

def discriminate_hard_instructions(student_scores: List[float], teacher_scores: List[float],
                                     threshold: float = 0.3) -> List[int]:
    hard = []
    for i, (s, t) in enumerate(zip(student_scores, teacher_scores)):
        if t - s > threshold: hard.append(i)
    return hard

def generate_harder_instructions(base_instructions: List[str], hard_indices: List[int]) -> List[str]:
    return [f"[HARDER] {base_instructions[i]}" for i in hard_indices if i < len(base_instructions)]

def distillation_loop_stats(n_iterations: int, student_acc: List[float], teacher_acc: List[float]) -> Dict:
    improvements = [s - student_acc[0] for s in student_acc]
    gaps = [t - s for t, s in zip(teacher_acc, student_acc)]
    return {"iterations": n_iterations, "final_student_acc": round(student_acc[-1], 4),
            "total_improvement": round(improvements[-1], 4), "final_gap": round(gaps[-1], 4)}
