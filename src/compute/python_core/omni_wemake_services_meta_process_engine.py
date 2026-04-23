from typing import Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniWemakeServicesMetaProcessEngine:
    """
    OmniWemakeServicesMetaProcessEngine
    
    Level-2 Abstraction for Repeatable Software Development Processes (assimilated from 'wemake-services/meta').
    Enforces Strict SDLC State Machine transitions using purely static graph analysis. 
    Prevents corrupt SDLC phase transitions like pushing to Production without CI validation.
    """

    # SDLC Strict Transition Directed Graph (From -> To)
    SDLC_TRANSITIONS = {
        "BACKLOG": {"IN_PROGRESS", "WONT_FIX"},
        "IN_PROGRESS": {"CODE_REVIEW", "BACKLOG"},
        "CODE_REVIEW": {"CI_PIPELINE", "IN_PROGRESS"},
        "CI_PIPELINE": {"STAGING_DEPLOY", "IN_PROGRESS"}, # Tests fail -> back to in_progress
        "STAGING_DEPLOY": {"QA", "CI_PIPELINE"},
        "QA": {"PROD_DEPLOY", "IN_PROGRESS"},
        "PROD_DEPLOY": {"DONE"},
        "DONE": set(),
        "WONT_FIX": set()
    }

    @classmethod
    def validate_process_transition(cls, current_stage: str, target_stage: str) -> Result[bool, Exception]:
        """
        Audits transition velocity across the SDLC finite state machine.
        
        Args:
            current_stage: The current process state node.
            target_stage: The proposed next process state node.
            
        Returns:
            Result[bool, Exception]: Ok if the transition adheres to the repeatable SDLC graph, 
            or Err if a stage skip or illegal traversal is attempted.
        """
        current_normalized = current_stage.upper().strip()
        target_normalized = target_stage.upper().strip()
        
        if current_normalized not in cls.SDLC_TRANSITIONS:
            return Err(Exception(f"SDLC Integrity Fault: Unknown origin stage '{current_stage}'."))
            
        allowed_targets = cls.SDLC_TRANSITIONS[current_normalized]
        
        if target_normalized in allowed_targets:
            return Ok(True)
        else:
            return Err(Exception(f"SDLC Violation: Illegal transition trajectory from '{current_normalized}' to '{target_normalized}'. Target unreachable directly."))

    @classmethod
    def diagnostics(cls) -> Dict[str, str]:
        return {
            "status": "operational",
            "mode": "Zero-Prod Static Transition Graph",
            "layer": "Domain",
            "rule": "Strict FSM SDLC Transitions"
        }
