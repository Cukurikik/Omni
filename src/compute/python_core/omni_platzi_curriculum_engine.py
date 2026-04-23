"""
OMNI Platzi Curriculum Engine.
Assimilated from: joelbarranteswins/Platzi-Courses
Provides: Sequence validation and progression path generation for data-science curriculums.
"""
from typing import Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

ENGINE_VERSION = "1.0.0-omni-platzi-curriculum"




class OmniPlatziCurriculumEngine:
    """
    Evaluates learning nodes recursively to establish logical progressions for data science competencies.
    
    @since 1.0.0
    @tags ["courses", "curriculum", "data-science", "jupyter"]
    """
    def __init__(self) -> None:
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        res = self.validate_progression(["MATH", "PYTHON", "PANDAS", "MACHINE_LEARNING"])
        if res.is_ok() and res.value["is_valid_sequence"]:
            return Ok({"engine": "PlatziCurriculum", "status": "Ready", "progression": "Functional"})
        return Err("Curriculum progression graph validation failed.")

    def validate_progression(self, course_nodes: List[str]) -> Result:
        """
        Calculates if a given linear path of courses meets strict prerequisite bounds.
        """
        if not course_nodes:
            return Err("Zero nodes exception. A curriculum must contain at least one node.")

        expected_order = {
            "MATH": 0,
            "PYTHON": 1,
            "PANDAS": 2,
            "MACHINE_LEARNING": 3,
            "DEEP_LEARNING": 4
        }

        current_level = -1
        
        for node in course_nodes:
            node_level = expected_order.get(node)
            if node_level is None:
                return Err(f"Unknown curriculum node sequence intercepted: {node}")
                
            if node_level < current_level:
                 return Ok({
                     "is_valid_sequence": False,
                     "reason": "PREREQUISITE_VIOLATION",
                     "current_max_node": "NEURAL_DEFICIT"
                 })
                 
            current_level = node_level

        return Ok({
            "is_valid_sequence": True,
            "nodes_processed": len(course_nodes),
            "max_competency_tier": current_level
        })
