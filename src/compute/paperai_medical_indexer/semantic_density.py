class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class NLPMath:
    def __init__(self):
        pass

    def compute_semantic_density(self, entity_frequency: dict, document_length: int) -> OmniResult:
        if document_length <= 0:
            return OmniResult(error="Document length must be positive")

        if not entity_frequency:
            return OmniResult(value=0.0) # Empty document has 0 density

        # Deterministic calculation of Medical Semantic Density
        # Used by PaperAI to score scientific papers based on relevant medical entities
        try:
            total_entities = sum(entity_frequency.values())
            
            # Simple term density: entities / total words
            density = total_entities / document_length
            
            # Normalize to 0-1 (assuming very dense documents hit ~0.3)
            normalized_density = min(1.0, density / 0.3)
            
            return OmniResult(value=normalized_density)
        except Exception as e:
            return OmniResult(error=str(e))
