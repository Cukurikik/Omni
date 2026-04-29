# OMNI Compute Layer - BOND NER Extractor
class BONDError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def extract_ner_distant_supervision(tokens: list, labels: list) -> Result:
    """Extracts Named Entities using Distant Supervision from RoBERTa soft-labels."""
    try:
        if len(tokens) != len(labels):
            return Result(error=BONDError("Tokens and labels length mismatch"))
            
        entities = [{"entity": t, "type": l} for t, l in zip(tokens, labels) if l != "O"]
        
        return Result(value={"entities": entities})
    except Exception as e:
        return Result(error=BONDError(f"BOND extraction failed: {str(e)}"))
