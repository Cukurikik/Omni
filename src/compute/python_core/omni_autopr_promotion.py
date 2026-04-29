# Omni AutoPR Academic Promotion Engine
# Ref: LightChen233/AutoPR — MIT
from typing import List, Dict

def extract_paper_features(paper: Dict) -> Dict:
    return {"title_len": len(paper.get("title", "").split()),
            "n_authors": len(paper.get("authors", [])),
            "has_code": paper.get("code_available", False),
            "venue_tier": paper.get("venue_tier", "unknown")}

def compute_promotion_score(papers: List[Dict], citations: List[int],
                              service: List[Dict]) -> Dict:
    pub_score = len(papers) * 2 + sum(1 for p in papers if p.get("venue_tier") in ["A*", "A"]) * 5
    cite_score = sum(min(c, 100) for c in citations) * 0.1
    service_score = len(service) * 1.5
    total = round(pub_score + cite_score + service_score, 2)
    return {"publication": pub_score, "citation": round(cite_score, 2),
            "service": service_score, "total": total}

def generate_cv_summary(features: Dict) -> str:
    return (f"Total publications: {features.get('n_papers', 0)}, "
            f"Citations: {features.get('total_citations', 0)}, "
            f"H-index: {features.get('h_index', 0)}")
