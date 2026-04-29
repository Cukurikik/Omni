import ray
import psutil
from typing import Dict, Any

class OmniResult:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error
    @classmethod
    def ok(cls, value: Any): return cls(True, value=value)
    @classmethod
    def err(cls, error: str): return cls(False, error=error)

class RayClusterLauncher:
    def __init__(self, num_cpus: int = None, num_gpus: int = None):
        self.num_cpus = num_cpus or psutil.cpu_count(logical=False)
        self.num_gpus = num_gpus
        
    def start_local_cluster(self) -> OmniResult:
        try:
            if ray.is_initialized():
                return OmniResult.err("Ray cluster is already initialized")
                
            init_kwargs = {
                "num_cpus": self.num_cpus,
                "ignore_reinit_error": True,
                "log_to_driver": False
            }
            if self.num_gpus is not None:
                init_kwargs["num_gpus"] = self.num_gpus
                
            ray.init(**init_kwargs)
            
            cluster_resources = ray.cluster_resources()
            return OmniResult.ok({
                "status": "Running",
                "cpus": cluster_resources.get("CPU", 0),
                "gpus": cluster_resources.get("GPU", 0),
                "nodes": len(ray.nodes())
            })
        except Exception as e:
            return OmniResult.err(f"Failed to start Ray cluster: {str(e)}")

    def shutdown(self) -> OmniResult:
        try:
            if not ray.is_initialized():
                return OmniResult.ok("Cluster already stopped")
            ray.shutdown()
            return OmniResult.ok("Cluster shut down successfully")
        except Exception as e:
            return OmniResult.err(f"Failed to shut down Ray cluster: {str(e)}")
