# OMNI Compute Layer - Kubeflow Training Operator
class KubeflowError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def generate_tfjob_spec(replicas: int, image: str) -> Result:
    """Generates TFJob CRD dict for Kubeflow."""
    try:
        if replicas < 1 or not image:
            return Result(error=KubeflowError("Invalid TFJob parameters"))
            
        spec = {
            "tfReplicaSpecs": {
                "Worker": {
                    "replicas": replicas,
                    "template": {"spec": {"containers": [{"image": image}]}}
                }
            }
        }
        
        return Result(value={"tfjob_spec": spec})
    except Exception as e:
        return Result(error=KubeflowError(f"Spec generation failed: {str(e)}"))
