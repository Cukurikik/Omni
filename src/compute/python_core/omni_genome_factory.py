from typing import List

class OmniGenomeFactory:
    """OMNI Compute Layer: Genome Factory for Genomic Models"""
    
    def __init__(self, kmer_size: int = 6):
        self.kmer = kmer_size

    def extract_kmers(self, sequence: str) -> List[str]:
        if not sequence or len(sequence) < self.kmer:
            return []
            
        kmers = []
        for i in range(len(sequence) - self.kmer + 1):
            kmers.append(sequence[i:i+self.kmer])
            
        return kmers
