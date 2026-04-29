from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniSrabonEngine(OmniBaseEngine):
    """
    Evaluates learning repetition cycles for sequential AI-generated educational
    states. Uses a deterministic logarithmic growth algorithm to compute recall intervals.
    """
    
    def __init__(self, base_interval: int = 1):
        super().__init__()
        self.base_interval = base_interval
        self.user_states: Dict[str, Dict[str, Any]] = {}

    def register_user(self, user_id: str) -> Result[bool, str]:
        """Perform register user computation.

            Args:
                    user_id: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if user_id in self.user_states:
            return Result.fail(f"Gamification bound breach: User '{user_id}' already registered.")
            
        self.user_states[user_id] = {
            "level": 1,
            "streaks": 0,
            "items": {} # memory_id -> { interval: int, next_review: int }
        }
        return Result.ok(True)

    def learn_item(self, user_id: str, item_id: str, current_time: int) -> Result[bool, str]:
        """
        Ingests a state node to track temporal repetitions.
        """
        if user_id not in self.user_states:
            return Result.fail("Unregistered entity execution denied.")
            
        repo = self.user_states[user_id]["items"]
        if item_id in repo:
            return Result.fail("Item structurally mapped already.")
            
        repo[item_id] = {
            "interval": self.base_interval,
            "next_review": current_time + self.base_interval,
            "reviews": 0
        }
        return Result.ok(True)

    def review_item(self, user_id: str, item_id: str, current_time: int, successful_recall: bool) -> Result[int, str]:
        """
        Updates pedagogical intervals deterministically computing SuperMemo SM-2 math constraints.
        """
        if user_id not in self.user_states:
            return Result.fail("Invalid topographical reference.")
            
        item_repo = self.user_states[user_id]["items"]
        if item_id not in item_repo:
            return Result.fail(f"Knowledge node '{item_id}' not found.")
            
        item_node = item_repo[item_id]
        if current_time < item_node["next_review"]:
            return Result.fail("Temporal constraint: Review executed prematurely.")
            
        item_node["reviews"] += 1
        
        if successful_recall:
            # Deterministic linear escalation metric
            item_node["interval"] = int(item_node["interval"] * 2.5)
            self.user_states[user_id]["streaks"] += 1
            if self.user_states[user_id]["streaks"] % 5 == 0:
                self.user_states[user_id]["level"] += 1
        else:
            # Degrade penalty
            item_node["interval"] = max(self.base_interval, int(item_node["interval"] * 0.5))
            self.user_states[user_id]["streaks"] = 0
            
        item_node["next_review"] = current_time + item_node["interval"]
        
        return Result.ok(item_node["next_review"])

    def get_due_items(self, user_id: str, current_time: int) -> Result[List[str], str]:
        """Perform get due items computation.

            Args:
                    user_id: str
                    current_time: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if user_id not in self.user_states:
            return Result.fail("Invalid reference scope.")
            
        due = []
        for item_id, data in self.user_states[user_id]["items"].items():
            if data["next_review"] <= current_time:
                due.append(item_id)
                
        # Sort deterministically
        due.sort()
        return Result.ok(due)

    def evaluate_gamified_learning_path(self, nodes: List[int]) -> Result[float, str]:
        """Perform evaluate gamified learning path computation.

            Args:
                    nodes: List[int]

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not nodes:
            return Result.fail("Empty path")
        score = sum(nodes) / len(nodes)
        return Result.ok(score)

    def diagnostics(self) -> dict:
        """Return engine diagnostic metadata.

        Returns:
            dict: Engine name, version, and operational status.
        """
        return {"engine": "OmniSrabonEngine", "version": "1.0.0", "status": "operational"}
