import hashlib

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class MerkleTreeMath:
    def __init__(self):
        pass

    def compute_directory_hash(self, file_hashes: dict[str, str]) -> OmniResult:
        if not file_hashes:
            return OmniResult(error="File hashes dict cannot be empty")

        # Deterministic Merkle Tree aggregation mimicking DVC .dir hash
        # Sort paths to ensure deterministic ordering
        sorted_paths = sorted(file_hashes.keys())
        
        hasher = hashlib.md5() # DVC uses MD5 extensively for performance
        
        for path in sorted_paths:
            f_hash = file_hashes[path]
            # Construct deterministic string: <hash>  <path>\n
            line = f"{f_hash}  {path}\n"
            hasher.update(line.encode('utf-8'))
            
        final_hash = hasher.hexdigest() + ".dir" # DVC specific suffix

        return OmniResult(value=final_hash)
