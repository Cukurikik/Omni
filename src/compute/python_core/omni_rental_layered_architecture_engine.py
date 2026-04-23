"""
OMNI Rental Layered Architecture Engine.
Assimilated from: AbdullahOztuurkk/Rent-A-Car-Project
Provides: Execute structural integrity checks across layered architecture application boundaries.
"""
from typing import Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

ENGINE_VERSION = "1.0.0-omni-rental-layered-architecture"




class OmniRentalLayeredArchitectureEngine:
    """
    Validates transactional object movement explicitly through Presentation -> Business -> Data Access strata.
    
    @since 1.0.0
    @tags ["c-sharp", "layered-architecture", "rental", "software-design"]
    """
    def __init__(self) -> None:
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        res = self.traverse_layer_boundaries(["UI", "BUSINESS", "DATA_ACCESS"])
        if res.is_ok() and res.value["transaction_committed"]:
            return Ok({"engine": "RentalLayeredArchitecture", "status": "Ready", "domain_strata": "Functional"})
        return Err("Architectural boundary breach detected in test sequence.")

    def traverse_layer_boundaries(self, traversal_record: List[str]) -> Result:
        """
        Calculates whether a transaction cleanly descended through the allowed architectural layers.
        """
        if not traversal_record:
            return Err("Empty transaction vector. No layers traversed.")

        valid_downward_path = ["UI", "BUSINESS", "DATA_ACCESS"]
        
        # A valid transaction must touch exactly these layers in exactly this order
        if len(traversal_record) != 3:
             return Ok({"transaction_committed": False, "violation": "INCOMPLETE_LAYER_REACH"})

        for i, layer in enumerate(traversal_record):
             if valid_downward_path[i] != layer:
                  return Ok({"transaction_committed": False, "violation": f"LAYER_BREACH_AT_{layer}"})

        return Ok({
            "transaction_committed": True,
            "layer_depth": 3,
            "violation": None
        })
