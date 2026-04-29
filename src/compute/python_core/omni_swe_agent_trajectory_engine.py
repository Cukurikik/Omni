"""OmniSWEAgentTrajectoryEngine.

Tracks and validates sequential terminal actions and environment
changes for the SWE-Agent software engineering trajectory logic.
"""
import sys
import os
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniSWEAgentTrajectoryEngine:
    """Zero-mock engine for SWE-Agent environment trajectory limits."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniSWEAgentTrajectoryEngine",
            "version": "1.0.0",
            "primitive": "agent_trajectory_tracker",
            "monadic_enforcement": True,
        }

    @staticmethod
    def analyze_action_trajectory(actions: List[Dict[str, Any]], max_steps: int = 15) -> Result:
        """
        Evaluates an agent's terminal action trajectory for loops or failures.
        """
        if not actions:
            return Err(ValueError("No actions to analyze"))
            
        action_types = [a.get("type", "unknown") for a in actions]
        
        # Check for catastrophic loops (e.g. 3 identical failing commands)
        loop_detected = False
        if len(action_types) >= 3:
            recent = action_types[-3:]
            if recent[0] == recent[1] == recent[2] and all(a.get("status") == "error" for a in actions[-3:]):
                loop_detected = True
                
        is_exhausted = len(actions) >= max_steps
        
        return Ok({
            "steps_taken": len(actions),
            "max_steps": max_steps,
            "is_exhausted": is_exhausted,
            "loop_detected": loop_detected,
            "unique_actions_used": len(set(action_types)),
            "requires_human_intervention": loop_detected or is_exhausted
        })
