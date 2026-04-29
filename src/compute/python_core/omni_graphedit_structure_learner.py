# Omni GraphEdit Structure Learner
# Compute Layer: LLM-guided graph structure learning with edit operations.
# Ref: HKUDS/GraphEdit — Graph Structure Learning with LLMs.
import hashlib, math
from typing import List, Dict, Set, Tuple

class AdjacencyGraph:
    def __init__(self):
        self.edges: Dict[str, Set[str]] = {}
    def add_node(self, node: str):
        if node not in self.edges:
            self.edges[node] = set()
    def add_edge(self, u: str, v: str):
        self.add_node(u); self.add_node(v)
        self.edges[u].add(v); self.edges[v].add(u)
    def remove_edge(self, u: str, v: str):
        if u in self.edges: self.edges[u].discard(v)
        if v in self.edges: self.edges[v].discard(u)
    def neighbors(self, node: str) -> Set[str]:
        return self.edges.get(node, set())
    def node_count(self) -> int:
        return len(self.edges)
    def edge_count(self) -> int:
        return sum(len(v) for v in self.edges.values()) // 2

def compute_edit_distance(graph_a: AdjacencyGraph, graph_b: AdjacencyGraph) -> int:
    all_nodes = set(graph_a.edges.keys()) | set(graph_b.edges.keys())
    edits = 0
    for n in all_nodes:
        na = graph_a.neighbors(n)
        nb = graph_b.neighbors(n)
        edits += len(na.symmetric_difference(nb))
    return edits // 2

def apply_edit_sequence(graph: AdjacencyGraph, edits: List[Dict]) -> Dict:
    applied = 0
    for edit in edits:
        op = edit.get("op", "")
        u, v = edit.get("u", ""), edit.get("v", "")
        if op == "add":
            graph.add_edge(u, v); applied += 1
        elif op == "remove":
            graph.remove_edge(u, v); applied += 1
    return {"applied": applied, "total_nodes": graph.node_count(), "total_edges": graph.edge_count()}

def graph_fingerprint(graph: AdjacencyGraph) -> str:
    edges_sorted = sorted((min(u, v), max(u, v)) for u in graph.edges for v in graph.edges[u])
    return hashlib.sha256(str(edges_sorted).encode()).hexdigest()[:16]
