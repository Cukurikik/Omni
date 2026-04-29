# Omni LLMs4OL Ontology Engine (Python)
# Compute Layer: LLM-based ontology learning with term typing and taxonomy discovery.
# Ref: HamedBabaei/LLMs4OL — LLMs for Ontology Learning.

from typing import List, Dict, Set, Tuple

class OntologyConcept:
    __slots__ = ('term', 'parent', 'confidence')
    def __init__(self, term: str, parent: str, confidence: float):
        self.term = term
        self.parent = parent
        self.confidence = max(0.0, min(1.0, confidence))

def build_taxonomy(concepts: List[OntologyConcept], min_confidence: float = 0.5) -> Dict[str, List[str]]:
    taxonomy: Dict[str, List[str]] = {}
    for c in concepts:
        if c.confidence < min_confidence:
            continue
        if c.parent not in taxonomy:
            taxonomy[c.parent] = []
        taxonomy[c.parent].append(c.term)
    return taxonomy

def detect_taxonomy_cycles(taxonomy: Dict[str, List[str]]) -> bool:
    visited: Set[str] = set()
    rec_stack: Set[str] = set()
    def dfs(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)
        for child in taxonomy.get(node, []):
            if child not in visited:
                if dfs(child):
                    return True
            elif child in rec_stack:
                return True
        rec_stack.discard(node)
        return False
    for node in taxonomy:
        if node not in visited:
            if dfs(node):
                return True
    return False
