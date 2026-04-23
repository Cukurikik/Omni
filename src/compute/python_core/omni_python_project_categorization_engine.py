from __future__ import annotations
from typing import Dict, Any, List, Set, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniPythonProjectCategorizationEngine:
    """
    omni-python-project-categorization
    
    A native matrix parsing component utilizing Jaccard Similarity formulas to dynamically 
    group uncategorized software project arrays mathematically by their tagging tokens.
    Inspired by Dhruv-Cmds/Python-Projects.
    """
    
    ENGINE_VERSION = "omni-s11-b4.1.0"
    
    def __init__(self, jaccard_threshold: float = 0.3) -> None:
        """Similarity threshold bounds before enforcing a split."""
        self.jaccard_threshold = jaccard_threshold

    def calculate_jaccard_similarity(self, set_a: Set[str], set_b: Set[str]) -> float:
        """Calculates Jaccard Index intuitively."""
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        if union == 0:
            return 0.0
        return intersection / union

    def dynamically_cluster_projects(self, projects_with_tags: List[Tuple[str, List[str]]]) -> Result:
        """
        Takes project matrix [("name", ["tag1", "tag2"])..] 
        Clusters them based on dynamic similarities mathematically.
        """
        try:
            if not projects_with_tags:
                return Err(ValueError("No valid token matrix arrays present to process categorizations."))
                
            clusters = [] # list of dicts {"centroid_tags": set, "projects": list}

            for p_name, tags in projects_with_tags:
                tags_set = set(tags)
                if not tags_set:
                    return Err(ValueError(f"Project bound '{p_name}' lacks categorical tags."))
                    
                best_cluster = None
                best_score = -1.0
                
                # Check against existing centroids
                for c in clusters:
                    score = self.calculate_jaccard_similarity(tags_set, c["centroid_tags"])
                    if score > best_score:
                        best_score = score
                        best_cluster = c
                        
                if best_score >= self.jaccard_threshold and best_cluster is not None:
                    # Append strictly to this structural cluster
                    best_cluster["projects"].append(p_name)
                    # Expand centroid tags uniquely
                    best_cluster["centroid_tags"].update(tags_set)
                else:
                    # Instantiate new structural categorical cluster
                    clusters.append({
                        "centroid_tags": tags_set,
                        "projects": [p_name]
                    })
                    
            # Export payload in standard data boundaries
            exported_clusters = []
            for idx, c in enumerate(clusters):
                exported_clusters.append({
                    "cluster_id": idx,
                    "representative_tags": list(c["centroid_tags"]),
                    "projects": c["projects"]
                })
                
            return Ok({"project_clusters": exported_clusters, "total_clusters": len(clusters)})
            
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Base Registry bindings."""
        return {
            "engine": "OmniPythonProjectCategorizationEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "threshold": self.jaccard_threshold,
            "complexity": "O(N * K) Sequential Clustering Node Matrix"
        }
