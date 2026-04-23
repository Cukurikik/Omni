from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniBmadOpenclawEngine:
    """
    OMNI Framework Level-2 Abstraction Engine.
    Assimilated from: ErwanLorteau/BMAD_Openclaw
    
    Purpose: Provides deterministic boundary validation for OpenCL memory 
    alignment mapping to prevent unaligned memory access crashes on GPU hardware.
    Also validates BMAD workflow state machine integrity.
    
    Enforces OMNI ZERO-MOCK Policy and Monadic Error Handling.
    """

    # Valid state transitions in the BMAD workflow FSM
    _VALID_TRANSITIONS = {
        "IDLE": ["PLAN"],
        "PLAN": ["DESIGN"],
        "DESIGN": ["BUILD"],
        "BUILD": ["VERIFY"],
        "VERIFY": ["DEPLOY", "DESIGN"],  # can loop back to DESIGN
        "DEPLOY": ["IDLE"],
    }

    @staticmethod
    def diagnostics() -> Dict[str, Any]:
        return {
            "engine": "OmniBmadOpenclawEngine",
            "status": "operational",
            "layer": "System",
            "abstraction_level": "L2-OpenCLMemoryAlignment",
            "monadic_enforcement": True
        }

    @staticmethod
    def validate_memory_alignment(buffer_size_bytes: int, hardware_alignment_bytes: int) -> 'Ok | Err':
        """
        Calculates whether an OpenCL buffer size natively aligns with hardware constraints,
        and computes the padded size if alignment is fractured.
        
        Args:
            buffer_size_bytes: Desired allocation size.
            hardware_alignment_bytes: Specific physical alignment requirement (e.g. 64, 128).
            
        Returns:
            Ok(padded_size) if calculable safely, or Err if hardware boundaries are corrupted.
        """
        try:
            if buffer_size_bytes <= 0:
                return Err(ValueError("Buffer size must be physically positive."))
            
            if hardware_alignment_bytes <= 0 or (hardware_alignment_bytes & (hardware_alignment_bytes - 1)) != 0:
                return Err(RuntimeError(f"Hardware alignment {hardware_alignment_bytes} violates power-of-2 physical constraint."))

            remainder = buffer_size_bytes % hardware_alignment_bytes
            
            if remainder == 0:
                return Ok(buffer_size_bytes)
                
            padding = hardware_alignment_bytes - remainder
            padded_size = buffer_size_bytes + padding
            
            return Ok(padded_size)

        except Exception as e:
            return Err(e)

    @classmethod
    def evaluate_workflow_integrity(cls, states: List[str]) -> 'Ok | Err':
        """
        Validates a sequence of BMAD workflow states against the deterministic FSM.
        
        Args:
            states: Ordered list of workflow states to validate.
            
        Returns:
            Ok with validated path if all transitions are legal, Err on illegal jumps.
        """
        try:
            if not states or len(states) < 2:
                return Err("Workflow must contain at least 2 states.")
            
            for i in range(len(states) - 1):
                current = states[i]
                next_state = states[i + 1]
                
                valid_nexts = cls._VALID_TRANSITIONS.get(current, [])
                if next_state not in valid_nexts:
                    return Err(f"Illegal state jump from '{current}' to '{next_state}' at position {i}.")
            
            return Ok({"valid": True, "path": states, "transitions": len(states) - 1})
        
        except Exception as e:
            return Err(str(e))


def __init__(self, value: Any):
        self.value = value
        self.is_ok = True

# Alias for test compatibility (Batch 5 uses uppercase C in 'Claw')
OmniBmadOpenClawEngine = OmniBmadOpenclawEngine
