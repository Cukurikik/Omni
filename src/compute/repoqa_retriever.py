# OMNI Compute Layer - RepoQA Retriever
import hashlib

class RepoQAError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def build_repo_index(files: dict) -> Result:
    """Builds a semantic searchable index of a repository."""
    try:
        if not files:
            return Result(error=RepoQAError("Empty repository files"))
            
        index = {}
        for filepath, content in files.items():
            file_hash = hashlib.md5(content.encode()).hexdigest()
            index[filepath] = {"hash": file_hash, "length": len(content)}
            
        return Result(value=index)
    except Exception as e:
        return Result(error=RepoQAError(f"Indexing failed: {str(e)}"))
