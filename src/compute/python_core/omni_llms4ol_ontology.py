# Omni LLMs4OL Ontology Learning Engine
# Ref: HamedBabaei/LLMs4OL
from typing import List, Tuple, Dict

def discover_taxonomic_relations(terms: List[str], embeddings: Dict[str, List[float]], similarity_threshold: float = 0.85) -> List[Tuple[str, str, float]]:
    """Discover hypernym-hyponym (is-a) relations based on embedding similarity and asymmetric distance."""
    relations = []
    
    for i, term_a in enumerate(terms):
        for j, term_b in enumerate(terms):
            if i == j:
                continue
                
            emb_a = embeddings.get(term_a)
            emb_b = embeddings.get(term_b)
            
            if not emb_a or not emb_b:
                continue
                
            # Cosine similarity
            dot = sum(a*b for a, b in zip(emb_a, emb_b))
            norm_a = sum(a*a for a in emb_a) ** 0.5
            norm_b = sum(b*b for b in emb_b) ** 0.5
            
            sim = dot / max(norm_a * norm_b, 1e-8)
            
            if sim > similarity_threshold:
                # Naive directional heuristic: shorter terms are often hypernyms of longer terms
                if len(term_a) < len(term_b):
                    relations.append((term_b, "is-a", term_a, round(sim, 4)))
                    
    return relations

def evaluate_ontology_precision(predicted_relations: List[Tuple[str, str, str]], ground_truth: List[Tuple[str, str, str]]) -> float:
    if not predicted_relations:
        return 0.0
    correct = len(set(predicted_relations) & set(ground_truth))
    return round(correct / len(predicted_relations), 4)
