# Omni DrugAssist Molecule Optimizer
# Compute Layer: LLM-based molecule optimization via SMILES manipulation.
# Ref: blazerye/DrugAssist — Briefings in Bioinformatics
import hashlib, math, re
from typing import Dict, List, Optional

ATOM_WEIGHTS = {"C": 12.011, "N": 14.007, "O": 15.999, "S": 32.065, "F": 18.998,
                "Cl": 35.453, "Br": 79.904, "I": 126.904, "P": 30.974, "H": 1.008}

def compute_molecular_weight(smiles: str) -> float:
    weight = 0.0
    i = 0
    while i < len(smiles):
        if i + 1 < len(smiles) and smiles[i:i+2] in ATOM_WEIGHTS:
            weight += ATOM_WEIGHTS[smiles[i:i+2]]; i += 2
        elif smiles[i] in ATOM_WEIGHTS:
            weight += ATOM_WEIGHTS[smiles[i]]; i += 1
        else:
            i += 1
    return round(weight, 3)

def lipinski_rule_of_five(mw: float, logp: float, hbd: int, hba: int) -> Dict:
    violations = 0
    if mw > 500: violations += 1
    if logp > 5: violations += 1
    if hbd > 5: violations += 1
    if hba > 10: violations += 1
    return {"passes": violations <= 1, "violations": violations, "mw": mw, "logp": logp, "hbd": hbd, "hba": hba}

def tanimoto_similarity(fp_a: set, fp_b: set) -> float:
    if not fp_a and not fp_b:
        return 1.0
    inter = len(fp_a & fp_b)
    union = len(fp_a | fp_b)
    return inter / union if union > 0 else 0.0

def smiles_fingerprint(smiles: str, ngram: int = 3) -> set:
    return {smiles[i:i+ngram] for i in range(max(0, len(smiles) - ngram + 1))}

def optimize_molecule(smiles: str, target_property: str, direction: str = "increase") -> Dict:
    mw = compute_molecular_weight(smiles)
    fp = smiles_fingerprint(smiles)
    return {"original_smiles": smiles, "molecular_weight": mw,
            "fingerprint_size": len(fp), "target": target_property, "direction": direction,
            "hash": hashlib.sha256(smiles.encode()).hexdigest()[:12]}
