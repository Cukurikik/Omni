# Omni Diagram of Thought Reasoning Engine
# Ref: diagram-of-thought/diagram-of-thought — arXiv:2409.10038
from typing import List, Dict

class ThoughtNode:
    def __init__(self, content: str, role: str, node_id: int):
        self.content = content; self.role = role; self.id = node_id
        self.children = []; self.critiques = []; self.score = 0.0

def build_dag(propositions: List[str], critiques: List[str], summaries: List[str]) -> List[Dict]:
    nodes = []
    nid = 0
    for p in propositions:
        nodes.append({"id": nid, "role": "proposer", "content": p, "children": []}); nid += 1
    for c in critiques:
        parent = (nid - len(critiques)) % max(len(propositions), 1)
        nodes.append({"id": nid, "role": "critic", "content": c, "parent": parent}); nid += 1
    for s in summaries:
        nodes.append({"id": nid, "role": "summarizer", "content": s}); nid += 1
    return nodes

def topos_coherence(dag: List[Dict]) -> float:
    if not dag: return 0
    roles = [n.get("role", "") for n in dag]
    valid_transitions = sum(1 for i in range(len(roles)-1)
                           if (roles[i], roles[i+1]) in {("proposer","critic"),("critic","proposer"),
                                                          ("critic","summarizer"),("proposer","summarizer")})
    return round(valid_transitions / max(len(roles)-1, 1), 4)

def reasoning_depth(dag: List[Dict]) -> int:
    proposer_count = sum(1 for n in dag if n.get("role") == "proposer")
    critic_count = sum(1 for n in dag if n.get("role") == "critic")
    return proposer_count + critic_count
