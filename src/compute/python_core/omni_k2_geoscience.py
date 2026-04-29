# Omni K2 Geoscience LLM Engine
# Ref: davendw49/k2 — Apache-2.0, WSDM 2024
from typing import List, Dict

GEO_DOMAINS = ["geology", "geophysics", "geochemistry", "hydrology", "oceanography",
               "atmospheric_science", "paleontology", "mineralogy", "seismology"]

def classify_geo_domain(question: str) -> str:
    q = question.lower()
    if any(w in q for w in ["earthquake", "seismic", "fault"]): return "seismology"
    if any(w in q for w in ["mineral", "crystal", "rock"]): return "mineralogy"
    if any(w in q for w in ["ocean", "sea", "marine"]): return "oceanography"
    if any(w in q for w in ["climate", "weather", "atmosphere"]): return "atmospheric_science"
    if any(w in q for w in ["water", "river", "aquifer"]): return "hydrology"
    if any(w in q for w in ["fossil", "dinosaur", "ancient"]): return "paleontology"
    return "geology"

def geo_benchmark_score(predictions: List[str], references: List[str]) -> Dict:
    correct = sum(1 for p, r in zip(predictions, references) if p.strip().lower() == r.strip().lower())
    return {"accuracy": round(correct / max(len(references), 1), 4), "n": len(references)}

def geosci_qa_format(question: str, choices: List[str]) -> str:
    opts = "\n".join(f"({chr(65+i)}) {c}" for i, c in enumerate(choices))
    return f"Question: {question}\n{opts}\nAnswer:"
