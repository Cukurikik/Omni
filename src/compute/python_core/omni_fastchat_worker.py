from typing import Dict, Any

class OmniFastChatWorker:
    """OMNI Compute Layer: FastChat Distributed Inference Worker"""
    
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.status = "idle"

    def assign_task(self, model_name: str, batch_size: int) -> Dict[str, Any]:
        self.status = "busy"
        
        # Deterministic capability check
        max_batch = 32 if "7b" in model_name.lower() else 8
        accepted_batch = min(batch_size, max_batch)
        
        return {
            "worker_id": self.worker_id,
            "assigned_model": model_name,
            "accepted_batch": accepted_batch,
            "status": "processing"
        }
