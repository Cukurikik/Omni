import hashlib

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class BlobHashing:
    def __init__(self):
        pass

    def compute_deterministic_hash(self, blob_bytes: bytes, metadata: dict) -> OmniResult:
        if blob_bytes is None:
            return OmniResult(error="Blob bytes cannot be null")

        # Deterministic hashing combining content and strictly ordered metadata
        # for Diffgram deduplication mechanism
        
        hasher = hashlib.sha256()
        hasher.update(blob_bytes)
        
        if metadata:
            # Sort metadata keys alphabetically to ensure deterministic hash output
            sorted_keys = sorted(metadata.keys())
            for key in sorted_keys:
                hasher.update(str(key).encode('utf-8'))
                hasher.update(str(metadata[key]).encode('utf-8'))
                
        final_hash = hasher.hexdigest()

        return OmniResult(value={
            "hash": final_hash,
            "bytes_processed": len(blob_bytes)
        })
