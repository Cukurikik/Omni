# Omni OceanGPT Domain Engine
# Ref: OceanGPT/OceanGPT — ACL 2024, MIT
# Implements: Ocean science QA, salinity/temperature modeling, domain classification
import math
from typing import List, Dict

OCEAN_DOMAINS = ["physical_oceanography", "marine_biology", "climate_science",
                  "ocean_chemistry", "marine_geology", "fisheries"]

def classify_ocean_domain(question: str) -> str:
    q = question.lower()
    if any(w in q for w in ["temperature", "current", "wave", "tide"]): return "physical_oceanography"
    if any(w in q for w in ["fish", "coral", "species", "ecosystem"]): return "marine_biology"
    if any(w in q for w in ["climate", "warming", "ice", "carbon"]): return "climate_science"
    if any(w in q for w in ["salinity", "ph", "oxygen", "nutrient"]): return "ocean_chemistry"
    return "physical_oceanography"

def compute_seawater_density(temperature: float, salinity: float, pressure: float = 0) -> float:
    rho_0 = 1027.0
    alpha = 0.00015; beta = 0.00078
    density = rho_0 * (1 - alpha * (temperature - 10) + beta * (salinity - 35) + 4.5e-7 * pressure)
    return round(density, 4)

def ocean_benchmark_score(predictions: List[str], references: List[str]) -> Dict:
    correct = sum(1 for p, r in zip(predictions, references) if p.strip().lower() == r.strip().lower())
    return {"accuracy": round(correct / max(len(references), 1), 6), "n": len(references)}
