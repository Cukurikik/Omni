"""OmniLearnlangEngine - Syntax divergence analysis with edit-distance grammar evaluation."""
from src.compute.python_core.omni_base_engine import Result, Ok, Err
class OmniLearnlangEngine:
    """OMNI Production Engine: OmniLearnlangEngine. Zero-Prod compliant."""
    def __init__(self):
        self.version = "3.6.0"
        
    def compute_syntax_divergence(self, base_grammar, sample_tokens):
        """Perform compute syntax divergence computation.

            Args:
                    base_grammar
                    sample_tokens

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not isinstance(base_grammar, list) or not isinstance(sample_tokens, list):
            return {"status": "error", "error": "Inputs must be lists of strictly typed string constraints."}
            
        exact_matches = 0
        divergence_accumulator = 0
        grammar_set = set(base_grammar)
        
        for token in sample_tokens:
            if token in grammar_set:
                exact_matches += 1
            else:
                # Calculate minimal exact char divergence without library dependency
                min_div = min([self._compute_edit_distance(token, rule) for rule in base_grammar]) if base_grammar else len(token)
                divergence_accumulator += min_div
                
        coverage_ratio = exact_matches / len(sample_tokens) if sample_tokens else 1.0
        
        return {
            "status": "ok",
            "value": {
                "coverage_ratio": round(coverage_ratio, 4),
                "exact_matches": exact_matches,
                "cumulative_divergence": divergence_accumulator
            }
        }
        
    def _compute_edit_distance(self, s1, s2):
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for index2, char2 in enumerate(s2):
            new_distances = [index2 + 1]
            for index1, char1 in enumerate(s1):
                if char1 == char2:
                    new_distances.append(distances[index1])
                else:
                    new_distances.append(1 + min((distances[index1], distances[index1+1], new_distances[-1])))
            distances = new_distances
        return distances[-1]

    def diagnostics(self):
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "version": self.version
        }

# Alias for test compatibility
OmniLearnLangEngine = OmniLearnlangEngine
