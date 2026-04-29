import hashlib

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class SHA256Hasher:
    def __init__(self):
        pass

    def compute_file_hash(self, file_content: bytes) -> OmniResult:
        if file_content is None:
            return OmniResult(error="Content cannot be None")

        # Deterministic SHA256 mimicking HuggingFace model blob hashing
        hasher = hashlib.sha256()
        hasher.update(file_content)
        
        return OmniResult(value=hasher.hexdigest())
