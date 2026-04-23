from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniSoftwareArchitectureDesignEngine:
    """
    Validates architectural layers and prevents dependency regressions entirely
    using a directed topology traversal model.
    """
    def __init__(self) -> None:
        self.components: Dict[str, int] = {}
        self.dependencies: Dict[str, List[str]] = {}

    def register_component(self, comp_id: str, layer: int) -> Result[bool, str]:
        """Perform register component computation.

            Args:
                    comp_id: str
                    layer: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not comp_id or comp_id in self.components:
            return Err("Invalid or duplicate component")
        if layer < 0:
            return Err("Layer must be positive")
            
        self.components[comp_id] = layer
        self.dependencies[comp_id] = []
        return Ok(True)

    def add_dependency(self, src: str, dest: str) -> Result[bool, str]:
        """Perform add dependency computation.

            Args:
                    src: str
                    dest: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if src not in self.components or dest not in self.components:
            return Err("Component not found")
            
        self.dependencies[src].append(dest)
        return Ok(True)

    def validate_layer_isolation(self) -> Result[bool, str]:
        """
        Validates that higher layers (higher integer) only depend on lower layers (lower integer)
        """
        for src, dests in self.dependencies.items():
            src_layer = self.components[src]
            for dest in dests:
                if self.components[dest] >= src_layer:
                    return Err(f"Layer violation: {src} -> {dest}")
        return Ok(True)

    def measure_coupling_factor(self) -> Result[float, str]:
        """Perform measure coupling factor computation.

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not self.components:
            return Err("No components registered")
        total_connections = sum(len(deps) for deps in self.dependencies.values())
        max_possible = len(self.components) * (len(self.components) - 1)
        if max_possible == 0:
            return Ok(0.0)
        return Ok(float(total_connections) / float(max_possible))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "components": len(self.components),
            "engine": "OmniSoftwareArchitectureDesignEngine"
        }
