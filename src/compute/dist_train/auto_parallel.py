import jax
import jax.numpy as jnp
from typing import Any, Tuple

class OmniResult:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error
    @classmethod
    def ok(cls, value: Any): return cls(True, value=value)
    @classmethod
    def err(cls, error: str): return cls(False, error=error)

class AutoParallelizer:
    def __init__(self, mesh_shape: Tuple[int, int]):
        self.mesh_shape = mesh_shape
        try:
            from jax.experimental import mesh_utils
            from jax.sharding import Mesh
            self.devices = mesh_utils.create_device_mesh(mesh_shape)
            self.mesh = Mesh(self.devices, axis_names=('dp', 'mp')) # Data parallel, Model parallel
        except Exception as e:
            self.mesh = None
            self.init_error = str(e)

    def partition_tensor(self, tensor: jnp.ndarray, partition_spec) -> OmniResult:
        if self.mesh is None:
            return OmniResult.err(f"Mesh not initialized: {self.init_error}")
            
        try:
            from jax.sharding import NamedSharding
            sharding = NamedSharding(self.mesh, partition_spec)
            sharded_tensor = jax.device_put(tensor, sharding)
            return OmniResult.ok(sharded_tensor)
        except Exception as e:
            return OmniResult.err(f"Tensor partitioning failed: {str(e)}")
