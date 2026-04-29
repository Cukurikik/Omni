class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class SemanticCommits:
    def __init__(self):
        pass

    def evaluate_commit_type(self, commit_message: str) -> OmniResult:
        if not commit_message:
            return OmniResult(error="Commit message cannot be empty")

        # Deterministic semantic commit matching
        # Used by the PR Review Bot to classify the type of changes in a pull request
        try:
            msg_lower = commit_message.lower()
            
            if msg_lower.startswith("feat:") or msg_lower.startswith("feat("):
                return OmniResult(value={"type": "feature", "semantic": True})
            elif msg_lower.startswith("fix:") or msg_lower.startswith("fix("):
                return OmniResult(value={"type": "bugfix", "semantic": True})
            elif msg_lower.startswith("chore:") or msg_lower.startswith("refactor:"):
                return OmniResult(value={"type": "maintenance", "semantic": True})
            
            return OmniResult(value={"type": "unknown", "semantic": False})
        except Exception as e:
            return OmniResult(error=str(e))
