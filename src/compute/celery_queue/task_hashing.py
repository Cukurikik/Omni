import hashlib

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class TaskHasher:
    def __init__(self):
        pass

    def compute_routing_key(self, task_name: str, args: list) -> OmniResult:
        if not task_name:
            return OmniResult(error="Task name cannot be empty")

        # Deterministic hashing for Celery task routing across worker nodes
        hasher = hashlib.md5()
        hasher.update(task_name.encode('utf-8'))
        
        for arg in args:
            # Simple string representation for hashing
            hasher.update(str(arg).encode('utf-8'))
            
        # Modulo against 16 queues deterministically
        digest_int = int(hasher.hexdigest(), 16)
        queue_id = digest_int % 16
        
        return OmniResult(value=f"queue_{queue_id}")
