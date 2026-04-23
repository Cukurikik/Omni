from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniVtta2008PlmEngine:
    """
    OMNI Framework Level-2 Abstraction Engine.
    Assimilated from: vtta2008/PLM

    Purpose: Pipeline Lifecycle Management. Validates production pipeline
    stage sequences (e.g., VFX/film pipelines) ensuring no stage is
    duplicated or out of mandatory order. Uses strict sequential
    invariant checking.
    Enforces OMNI ZERO-MOCK Policy and Monadic Error Handling.
    """

    @staticmethod
    def diagnostics() -> Dict[str, Any]:
        return {
            "engine": "OmniVtta2008PlmEngine",
            "status": "operational",
            "layer": "Compute",
            "abstraction_level": "L2-PipelineLifecycle",
            "monadic_enforcement": True
        }

    @staticmethod
    def validate_pipeline_stages(stages: List[str], mandatory_order: List[str]) -> Result[bool, Exception]:
        """
        Validates that all mandatory stages appear in the pipeline in the correct
        relative order, with no duplicates.
        """
        if not stages:
            return Err(ValueError("Pipeline stages list cannot be empty."))
        if not mandatory_order:
            return Err(ValueError("Mandatory order list cannot be empty."))

        # Check for duplicates
        if len(stages) != len(set(stages)):
            seen = set()
            for s in stages:
                if s in seen:
                    return Err(RuntimeError(f"Duplicate pipeline stage detected: '{s}'"))
                seen.add(s)

        # Check mandatory stages are present and in correct relative order
        stage_positions = {s: i for i, s in enumerate(stages)}
        last_pos = -1
        for mandatory_stage in mandatory_order:
            if mandatory_stage not in stage_positions:
                return Err(ValueError(f"Missing mandatory pipeline stage: '{mandatory_stage}'"))
            current_pos = stage_positions[mandatory_stage]
            if current_pos <= last_pos:
                return Err(RuntimeError(
                    f"Pipeline order violation: '{mandatory_stage}' must appear after "
                    f"previous mandatory stage in sequence."
                ))
            last_pos = current_pos

        return Ok(True)
