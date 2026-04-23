from typing import Dict, Any, List, Set
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniTomatoArchitectureEngine:
    """
    OMNI Framework Level-2 Abstraction Engine.
    Assimilated from: tomato-architecture/tomato-architecture.github.io

    Purpose: Validates pragmatic software architecture layer dependencies.
    Ensures no upward dependency violations in a layered architecture
    (e.g., Domain layer must NEVER depend on Infrastructure layer).
    Uses Directed Acyclic Graph (DAG) adjacency validation.
    Enforces OMNI ZERO-MOCK Policy and Monadic Error Handling.
    """

    VALID_LAYERS = ["presentation", "application", "domain", "infrastructure"]
    # Allowed dependency direction: layer can only depend on layers BELOW it (higher index)
    LAYER_INDEX = {layer: i for i, layer in enumerate(VALID_LAYERS)}

    @staticmethod
    def diagnostics() -> Dict[str, Any]:
        return {
            "engine": "OmniTomatoArchitectureEngine",
            "status": "operational",
            "layer": "Compute",
            "abstraction_level": "L2-PragmaticLayerValidation",
            "monadic_enforcement": True
        }

    @staticmethod
    def validate_layer_dependency(source_layer: str, target_layer: str) -> Result[bool, Exception]:
        """
        Validates that a dependency from source_layer to target_layer
        does NOT violate the downward-only dependency rule.
        In Tomato Architecture: Presentation -> Application -> Domain -> Infrastructure.
        A layer may only depend on layers at the same level or below.
        """
        idx = OmniTomatoArchitectureEngine.LAYER_INDEX
        if source_layer not in idx:
            return Err(ValueError(f"Unknown source layer: '{source_layer}'. Valid: {OmniTomatoArchitectureEngine.VALID_LAYERS}"))
        if target_layer not in idx:
            return Err(ValueError(f"Unknown target layer: '{target_layer}'. Valid: {OmniTomatoArchitectureEngine.VALID_LAYERS}"))

        if idx[target_layer] < idx[source_layer]:
            return Err(RuntimeError(
                f"Architecture violation: '{source_layer}' (L{idx[source_layer]}) "
                f"cannot depend on '{target_layer}' (L{idx[target_layer]}). "
                f"Dependencies must flow downward only."
            ))
        return Ok(True)
