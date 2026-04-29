from typing import List, Dict

class OmniVoyagerSkills:
    """OMNI Compute Layer: Voyager Minecraft Skill Library Manager"""
    
    def __init__(self):
        self.skills: Dict[str, str] = {}

    def add_skill(self, name: str, code: str) -> bool:
        if name in self.skills:
            return False
        self.skills[name] = code
        return True

    def retrieve_relevant_skills(self, task_description: str, top_k: int = 2) -> List[str]:
        # Deterministic substring heuristic
        relevant = []
        task_lower = task_description.lower()
        
        for name in self.skills.keys():
            if name.lower() in task_lower:
                relevant.append(name)
                
        # If not enough, append others
        for name in self.skills.keys():
            if name not in relevant:
                relevant.append(name)
            if len(relevant) >= top_k:
                break
                
        return relevant[:top_k]
