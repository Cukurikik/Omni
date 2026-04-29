class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class RAGMetrics:
    def __init__(self):
        pass

    def compute_mrr(self, relevant_doc_positions: list[int]) -> OmniResult:
        if not relevant_doc_positions:
            return OmniResult(error="Positions list cannot be empty")
        
        for pos in relevant_doc_positions:
            if pos <= 0:
                return OmniResult(error="Document positions must be 1-indexed and positive")

        # Deterministic Mean Reciprocal Rank (MRR) for RAG retrieval evaluation
        try:
            mrr = sum(1.0 / pos for pos in relevant_doc_positions) / len(relevant_doc_positions)
            return OmniResult(value=mrr)
        except Exception as e:
            return OmniResult(error=str(e))
