# @omni-layer Infrastructure | @omni-lang Pulumi/Python | @omni-batch 18 | @omni-semester 16
# @omni-description Pulumi IaC for multi-cloud transformer deployment:
# GCP GKE cluster with GPU node pools and model serving.

import json

class PulumiConfig:
    """Pulumi configuration for OMNI transformer multi-cloud deployment."""

    def __init__(self, project: str = "omni-transformer", stack: str = "production"):
        self.project = project
        self.stack = stack

    def gke_cluster(self, name: str = "omni-inference", region: str = "us-central1") -> dict:
        return {
            "resource_type": "gcp:container:Cluster",
            "name": name,
            "properties": {
                "location": region,
                "initial_node_count": 1,
                "remove_default_node_pool": True,
                "networking_mode": "VPC_NATIVE",
                "ip_allocation_policy": {},
                "release_channel": {"channel": "STABLE"},
                "workload_identity_config": {"workload_pool": f"{self.project}.svc.id.goog"},
            },
        }

    def gpu_node_pool(self, cluster_name: str, gpu_type: str = "nvidia-tesla-t4") -> dict:
        return {
            "resource_type": "gcp:container:NodePool",
            "name": f"{cluster_name}-gpu-pool",
            "properties": {
                "cluster": cluster_name,
                "node_count": 2,
                "autoscaling": {"min_node_count": 1, "max_node_count": 8},
                "node_config": {
                    "machine_type": "n1-standard-8",
                    "disk_size_gb": 200,
                    "oauth_scopes": ["https://www.googleapis.com/auth/cloud-platform"],
                    "guest_accelerators": [{"type": gpu_type, "count": 1}],
                    "labels": {"workload": "transformer-inference", "batch": "18"},
                    "taints": [{"key": "nvidia.com/gpu", "value": "present", "effect": "NO_SCHEDULE"}],
                },
            },
        }

    def model_serving(self, name: str = "omni-serving") -> dict:
        return {
            "resource_type": "kubernetes:apps/v1:Deployment",
            "name": name,
            "properties": {
                "metadata": {"name": name, "labels": {"app": "omni-transformer"}},
                "spec": {
                    "replicas": 2,
                    "selector": {"matchLabels": {"app": "omni-transformer"}},
                    "template": {
                        "metadata": {"labels": {"app": "omni-transformer"}},
                        "spec": {
                            "containers": [{
                                "name": "inference",
                                "image": "omni/transformer-inference:1.0.0",
                                "ports": [{"containerPort": 8080}],
                                "resources": {
                                    "requests": {"cpu": "2", "memory": "8Gi", "nvidia.com/gpu": "1"},
                                    "limits": {"cpu": "4", "memory": "16Gi", "nvidia.com/gpu": "1"},
                                },
                                "env": [
                                    {"name": "MODEL_DIR", "value": "/models"},
                                    {"name": "MAX_BATCH_SIZE", "value": "32"},
                                ],
                                "readiness_probe": {
                                    "httpGet": {"path": "/health", "port": 8080},
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10,
                                },
                            }],
                            "tolerations": [{"key": "nvidia.com/gpu", "operator": "Exists", "effect": "NoSchedule"}],
                        },
                    },
                },
            },
        }

    def export_stack(self) -> str:
        stack = {
            "project": self.project,
            "stack": self.stack,
            "resources": [
                self.gke_cluster(),
                self.gpu_node_pool("omni-inference"),
                self.model_serving(),
            ],
        }
        return json.dumps(stack, indent=2)
