import random
from typing import List

class AgentSkillEvolver:
    def __init__(self, population_size: int = 10):
        self.population_size = population_size
        self.skills = []
        
    def mutate_skill(self, skill_prompt: str) -> str:
        mutations = [
            " Think step by step.",
            " Be highly concise.",
            " Verify the answer."
        ]
        return skill_prompt + random.choice(mutations)
        
    def evolve(self, prompts: List[str], scores: List[float]) -> str:
        best_idx = np.argmax(scores) if type(scores) == list else 0
        return self.mutate_skill(prompts[best_idx])
