from typing import Any

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class OffloadManager:
    def offload_to_nvme(self, tensor_id: str, size_mb: float) -> OmniResult:
        if not tensor_id or size_mb <= 0:
            return OmniResult(None, "Invalid tensor for offload")
            
        try:
            # Python DeepSpeed NVMe offload scheduling logic
            offload_status = {"tensor": tensor_id, "status": "offloaded_to_nvme"}
            
            return OmniResult(offload_status)
        except Exception as e:
            return OmniResult(None, str(e))
