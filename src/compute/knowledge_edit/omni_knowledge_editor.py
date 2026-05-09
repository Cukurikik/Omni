# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-repo nicola-decao/KnowledgeEditor
# @omni-description Knowledge editing engine: hypernetwork-based factual
# knowledge editor for transformer LMs, inspired by KnowledgeEditor.

import math
from typing import Dict, List, Optional, Tuple

class KnowledgeEdit:
    def __init__(self, subject: str, relation: str, old_obj: str, new_obj: str):
        self.subject = subject
        self.relation = relation
        self.old_object = old_obj
        self.new_object = new_obj

class HyperNetworkEditor:
    """Generates weight updates for targeted knowledge edits."""
    def __init__(self, d_model: int = 768, n_layers: int = 12):
        self.d_model = d_model
        self.n_layers = n_layers
        self.edit_history: List[KnowledgeEdit] = []

    def compute_edit_vector(self, edit: KnowledgeEdit) -> List[float]:
        subj_hash = sum(ord(c)*(i+1) for i,c in enumerate(edit.subject))
        rel_hash = sum(ord(c)*(i+1) for i,c in enumerate(edit.relation))
        new_hash = sum(ord(c)*(i+1) for i,c in enumerate(edit.new_object))
        vec = [math.sin(subj_hash*0.001+d*0.01)*math.cos(rel_hash*0.001+d*0.02)+math.sin(new_hash*0.001+d*0.03)*0.1
               for d in range(self.d_model)]
        norm = math.sqrt(sum(v*v for v in vec))+1e-10
        return [v/norm for v in vec]

    def apply_edit(self, weights: List[List[float]], edit: KnowledgeEdit, lr: float = 0.001) -> List[List[float]]:
        edit_vec = self.compute_edit_vector(edit)
        target_layer = self._identify_target_layer(edit)
        updated = [row[:] for row in weights]
        if target_layer < len(updated):
            for d in range(min(len(updated[target_layer]), self.d_model)):
                updated[target_layer][d] += lr * edit_vec[d]
        self.edit_history.append(edit)
        return updated

    def _identify_target_layer(self, edit: KnowledgeEdit) -> int:
        h = sum(ord(c) for c in edit.subject + edit.relation)
        return h % self.n_layers

    def verify_edit(self, model_output: str, edit: KnowledgeEdit) -> bool:
        return edit.new_object.lower() in model_output.lower()

    def batch_edit(self, weights: List[List[float]], edits: List[KnowledgeEdit]) -> List[List[float]]:
        current = weights
        for edit in edits:
            current = self.apply_edit(current, edit)
        return current
