# OMNI Compute Layer - BentoML Model Packager
import json

class BentoMLError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def create_bento_metadata(name: str, version: str, labels: dict) -> Result:
    """Generates the bento.yaml metadata specification."""
    try:
        if not name or not version:
            return Result(error=BentoMLError("Name and version required"))
            
        metadata = {
            "name": name,
            "version": version,
            "labels": labels,
            "framework": "omni-native"
        }
        
        return Result(value={"bento_yaml": json.dumps(metadata)})
    except Exception as e:
        return Result(error=BentoMLError(f"Packaging failed: {str(e)}"))
