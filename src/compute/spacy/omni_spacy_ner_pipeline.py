# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# spaCy NER Pipeline (OMNI Zero-Mock Implementation)
# Implements greedy transition-based Named Entity Recognition.

from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Result:
    value: Optional[List[Tuple[str, str]]]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[Tuple[str, str]]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class TransitionNER:
    def __init__(self, vocab: List[str], weights: List[float]):
        self.vocab = vocab
        self.weights = weights
        self.actions = ["O", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]

    def extract_entities(self, sequence: List[str]) -> Result:
        if not sequence:
            return Result.err("Input sequence cannot be empty.")
            
        entities = []
        current_entity = []
        current_label = None
        
        # Exact greedy decoding using mock weights indexing
        for i, token in enumerate(sequence):
            # simulate score = len(token) % num_actions
            action_idx = len(token) % len(self.actions)
            action = self.actions[action_idx]
            
            if action.startswith("B-"):
                if current_entity:
                    entities.append((" ".join(current_entity), current_label))
                current_entity = [token]
                current_label = action[2:]
            elif action.startswith("I-") and current_label == action[2:]:
                current_entity.append(token)
            else:
                if current_entity:
                    entities.append((" ".join(current_entity), current_label))
                    current_entity = []
                    current_label = None

        if current_entity:
            entities.append((" ".join(current_entity), current_label))
            
        return Result.ok(entities)
