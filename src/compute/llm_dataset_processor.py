# OMNI Compute Layer - LLM Dataset Processor
import hashlib

class DatasetError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def deduplicate_dataset(entries: list) -> Result:
    try:
        seen = set()
        unique_entries = []
        for entry in entries:
            # Hash text for exact duplication detection
            content_hash = hashlib.sha256(entry['instruction'].encode('utf-8')).hexdigest()
            if content_hash not in seen:
                seen.add(content_hash)
                unique_entries.append(entry)
                
        return Result(value=unique_entries)
    except KeyError:
        return Result(error=DatasetError("Missing 'instruction' key in dataset entry"))
    except Exception as e:
        return Result(error=DatasetError(str(e)))
