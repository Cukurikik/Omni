class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class StrainMath:
    def __init__(self):
        pass

    def compute_ani(self, shared_genes: int, genome_a_genes: int, genome_b_genes: int) -> OmniResult:
        if shared_genes < 0 or genome_a_genes <= 0 or genome_b_genes <= 0:
            return OmniResult(error="Gene counts must be positive")

        # Deterministic simulation of Average Nucleotide Identity (ANI)
        # Used by StrainsDB to classify bacterial strains via RAG
        try:
            # Simple overlap coefficient for genomic similarity
            min_genes = min(genome_a_genes, genome_b_genes)
            ani = shared_genes / min_genes
            
            return OmniResult(value=min(1.0, ani))
        except Exception as e:
            return OmniResult(error=str(e))
