# OMNI Compute Layer - KubeRay Cluster Spec
class KubeRayError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def generate_raycluster_manifest(name: str, worker_nodes: int) -> Result:
    """Generates K8s YAML dict for KubeRay operator."""
    try:
        if worker_nodes < 0:
            return Result(error=KubeRayError("Worker nodes cannot be negative"))
            
        manifest = {
            "apiVersion": "ray.io/v1",
            "kind": "RayCluster",
            "metadata": {"name": name},
            "spec": {
                "headGroupSpec": {"replicas": 1},
                "workerGroupSpecs": [{"replicas": worker_nodes, "groupName": "small-group"}]
            }
        }
        
        return Result(value={"manifest": manifest})
    except Exception as e:
        return Result(error=KubeRayError(f"Manifest generation failed: {str(e)}"))
