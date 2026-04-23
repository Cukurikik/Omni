from __future__ import annotations
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniCSEProjectsCurationEngine:
    """
    omni-cse-projects-curation
    
    Natively groups computational dataset domains mapping tag overlap logic structures
    resembling recommendation clustering natively without heavy external bounds architectures.
    """
    
    ENGINE_VERSION = "omni-s11-b6.1.0"
    
    def __init__(self) -> None:
        self.categorizations = 0

    def categorize_project_matrix(self, projects: List[Dict[str, Any]], predefined_domains: Dict[str, List[str]]) -> Result:
        """
        projects format: [{"name": "AuthSys", "tags": ["security", "database"]}, ...]
        predefined_domains: {"Cybersecurity": ["security", "crypto"], "Web": ["api", "frontend"]}
        Computes the best bounding mapping natively through Jaccard-like intersection scores.
        """
        try:
            if not projects or not predefined_domains:
                return Err(ValueError("Cannot cluster empty metric structures structurally!"))
                
            clustered_output = {domain: [] for domain in predefined_domains.keys()}
            clustered_output["Uncategorized"] = []
            
            # Native topological clustering matrix logic bounds
            for item in projects:
                if "name" not in item or "tags" not in item:
                    return Err(ValueError("Structural boundaries require 'name' and 'tags' sequence arrays!"))
                    
                tags_set = set(item["tags"])
                
                best_domain = "Uncategorized"
                best_score = 0
                
                for domain_name, domain_tags in predefined_domains.items():
                    d_tags_set = set(domain_tags)
                    # intersection bounds ratio
                    overlap = len(tags_set.intersection(d_tags_set))
                    if overlap > best_score:
                        best_score = overlap
                        best_domain = domain_name
                        
                clustered_output[best_domain].append(item["name"])
                self.categorizations += 1
                
            return Ok({
                "clusters": clustered_output,
                "total_projects": len(projects)
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides native domain bounding verifications limit."""
        return {
            "engine": "OmniCSEProjectsCurationEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "mapped_items": self.categorizations,
            "complexity": "O(N * D) Linear Overlap Grouping Limit"
        }
