# Omni SubgraphRAG Knowledge-Graph RAG Engine
# Ref: Graph-COM/SubgraphRAG — ICLR'25 | MIT
# KG-based retrieval-augmented generation via subgraph extraction
import math
from typing import List, Dict, Tuple, Set

def build_adjacency(triples: List[Tuple[str, str, str]]) -> Dict[str, List[Tuple[str, str]]]:
    """Build adjacency list from knowledge graph triples (h, r, t)."""
    adj: Dict[str, List[Tuple[str, str]]] = {}
    for h, r, t in triples:
        adj.setdefault(h, []).append((r, t))
        adj.setdefault(t, []).append((r + "_inv", h))
    return adj

def extract_subgraph(adj: Dict, seed_entities: List[str], max_hops: int = 2) -> List[Tuple[str, str, str]]:
    """Extract k-hop subgraph around seed entities."""
    visited: Set[str] = set(seed_entities)
    frontier = list(seed_entities)
    subgraph_triples = []
    for hop in range(max_hops):
        next_frontier = []
        for node in frontier:
            for rel, neighbor in adj.get(node, []):
                subgraph_triples.append((node, rel, neighbor))
                if neighbor not in visited:
                    visited.add(neighbor)
                    next_frontier.append(neighbor)
        frontier = next_frontier
    return subgraph_triples

def entity_link(query: str, entity_vocab: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
    """Simple token-overlap entity linking from query to KG entities."""
    query_tokens = set(query.lower().split())
    scored = []
    for ent in entity_vocab:
        ent_tokens = set(ent.lower().replace("_", " ").split())
        overlap = len(query_tokens & ent_tokens)
        score = overlap / max(len(ent_tokens), 1)
        if score > 0:
            scored.append((ent, round(score, 4)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]

def subgraph_to_context(triples: List[Tuple[str, str, str]], max_triples: int = 50) -> str:
    """Convert subgraph triples to textual context for LLM."""
    lines = [f"{h} --[{r}]--> {t}" for h, r, t in triples[:max_triples]]
    return "\n".join(lines)

def evaluate_kgqa(predictions: List[str], gold_answers: List[List[str]]) -> Dict:
    """Evaluate KG-QA with hit@1 and F1."""
    hits = 0
    for pred, golds in zip(predictions, gold_answers):
        if any(g.lower() in pred.lower() for g in golds):
            hits += 1
    return {"hit_at_1": round(hits / max(len(predictions), 1), 4), "n_samples": len(predictions)}
