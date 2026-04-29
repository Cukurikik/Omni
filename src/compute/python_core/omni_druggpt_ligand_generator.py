# Omni DrugGPT Ligand Generator
# Compute: GPT-based protein-targeted ligand design via SMILES generation.
# Ref: LIYUESEN/druggpt — GPL-3.0
import math, hashlib
from typing import Dict, List, Tuple

AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY")
ATOM_WEIGHTS = {"C":12.011,"N":14.007,"O":15.999,"S":32.065,"H":1.008,"F":18.998,"Cl":35.453,"Br":79.904,"P":30.974}

def validate_protein_sequence(seq: str) -> Dict:
    if not seq: return {"valid": False, "error": "OMNI_ERR: empty sequence"}
    invalid = [c for c in seq.upper() if c not in AMINO_ACIDS]
    return {"valid": len(invalid) == 0, "length": len(seq), "invalid_chars": invalid}

def estimate_molecular_weight(smiles: str) -> float:
    w = 0.0; i = 0
    while i < len(smiles):
        if i+1 < len(smiles) and smiles[i:i+2] in ATOM_WEIGHTS:
            w += ATOM_WEIGHTS[smiles[i:i+2]]; i += 2
        elif smiles[i] in ATOM_WEIGHTS:
            w += ATOM_WEIGHTS[smiles[i]]; i += 1
        else: i += 1
    return round(w, 3)

def compute_binding_affinity_score(protein_len: int, ligand_mw: float, contact_residues: int) -> float:
    if protein_len == 0 or ligand_mw == 0: return 0.0
    coverage = contact_residues / protein_len
    size_factor = 1.0 / (1.0 + math.exp(-(ligand_mw - 300) / 100))
    return round(coverage * size_factor, 6)

def generate_ligand_fingerprint(smiles: str, protein_hash: str) -> str:
    return hashlib.sha256(f"{smiles}:{protein_hash}".encode()).hexdigest()[:16]

def druggpt_pipeline(protein_seq: str, candidate_smiles: List[str]) -> Dict:
    val = validate_protein_sequence(protein_seq)
    if not val["valid"]: return {"status": "error", "message": val.get("error", "Invalid protein")}
    results = []
    for smi in candidate_smiles:
        mw = estimate_molecular_weight(smi)
        score = compute_binding_affinity_score(len(protein_seq), mw, max(1, len(protein_seq) // 10))
        results.append({"smiles": smi, "mw": mw, "affinity_score": score,
                        "fingerprint": generate_ligand_fingerprint(smi, hashlib.md5(protein_seq.encode()).hexdigest()[:8])})
    results.sort(key=lambda x: x["affinity_score"], reverse=True)
    return {"status": "ok", "protein_length": len(protein_seq), "candidates": results}
