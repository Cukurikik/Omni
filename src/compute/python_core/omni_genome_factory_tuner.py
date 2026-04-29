# Omni Genome Factory Tuner
# Compute: Genomic foundation model fine-tuning and interpretation.
# Ref: WeiminWu2000/Genome_Factory
import math
from typing import Dict, List

DNA_BASES = set("ACGT")
CODON_TABLE = {"ATG":"Met","TAA":"Stop","TAG":"Stop","TGA":"Stop","GCT":"Ala","TGT":"Cys"}

def validate_dna_sequence(seq: str) -> Dict:
    invalid = [c for c in seq.upper() if c not in DNA_BASES]
    return {"valid": len(invalid) == 0, "length": len(seq), "gc_content": round(
        (seq.upper().count('G') + seq.upper().count('C')) / max(len(seq), 1), 6)}

def kmer_frequency(seq: str, k: int = 6) -> Dict[str, int]:
    freq = {}
    for i in range(len(seq) - k + 1):
        kmer = seq[i:i+k].upper()
        freq[kmer] = freq.get(kmer, 0) + 1
    return freq

def compute_lora_params(base_params: int, rank: int, n_layers: int) -> Dict:
    lora_params = 2 * rank * (base_params // n_layers) * n_layers
    ratio = lora_params / max(base_params, 1)
    return {"lora_params": lora_params, "base_params": base_params, "ratio": round(ratio, 6)}
