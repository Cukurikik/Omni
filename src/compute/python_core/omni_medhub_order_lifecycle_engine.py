"""OmniMedhubOrderLifecycleEngine — Order State Machine & Audit Trail.

Inspired by Abdalrahman-Alhamod/MedHub-Mobile: a Flutter/Laravel
pharmaceutical management app with order tracking, medicine browsing,
and multi-language support.

Algorithmic Primitive:
    Implement a Finite State Machine (FSM) for pharmaceutical order
    lifecycle management. Enforce valid state transitions (e.g.
    pending → confirmed → shipped → delivered), reject invalid
    transitions, and maintain an immutable audit trail of all
    state changes.
"""
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from __future__ import annotations
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniMedhubOrderLifecycleEngine:
    """Production-grade order lifecycle FSM with audit trail."""

    # Valid state transitions: current_state -> set of allowed next states
    TRANSITION_TABLE: dict[str, set[str]] = {
        "pending":    {"confirmed", "cancelled"},
        "confirmed":  {"processing", "cancelled"},
        "processing": {"shipped", "cancelled"},
        "shipped":    {"delivered", "returned"},
        "delivered":  {"returned"},
        "cancelled":  set(),
        "returned":   {"refunded"},
        "refunded":   set(),
    }

    ALL_STATES = set(TRANSITION_TABLE.keys())

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniMedhubOrderLifecycleEngine",
            "version": "1.0.0",
            "primitive": "finite_state_machine_order_lifecycle",
            "monadic_enforcement": True,
            "source_repo": "Abdalrahman-Alhamod/MedHub-Mobile",
        }

    @staticmethod
    def validate_transition(current_state: str, target_state: str) -> Result:
        """Check if a state transition is valid.

        Args:
            current_state: The current order state.
            target_state: The desired next state.

        Returns:
            Result[bool, Exception]: True if valid, Err if invalid.
        """
        if current_state not in OmniMedhubOrderLifecycleEngine.ALL_STATES:
            return Err(Exception(f"Unknown state: '{current_state}'"))
        if target_state not in OmniMedhubOrderLifecycleEngine.ALL_STATES:
            return Err(Exception(f"Unknown state: '{target_state}'"))

        allowed = OmniMedhubOrderLifecycleEngine.TRANSITION_TABLE[current_state]
        if target_state in allowed:
            return Ok(True)
        else:
            return Err(Exception(
                f"Invalid transition: '{current_state}' → '{target_state}'. "
                f"Allowed: {sorted(allowed) if allowed else 'none (terminal state)'}"
            ))

    @staticmethod
    def apply_transitions(
        initial_state: str,
        transitions: list[str],
    ) -> Result:
        """Apply a sequence of transitions and return audit trail.

        Args:
            initial_state: Starting state of the order.
            transitions: List of target states to transition to in sequence.

        Returns:
            Result[dict, Exception]: dict with 'final_state',
            'audit_trail' (list of transition records),
            'transition_count'.
        """
        if initial_state not in OmniMedhubOrderLifecycleEngine.ALL_STATES:
            return Err(Exception(f"Unknown initial state: '{initial_state}'"))
        if not isinstance(transitions, list):
            return Err(Exception("transitions must be a list"))

        current = initial_state
        audit_trail: list[dict] = [{"step": 0, "state": current, "action": "initial"}]

        for i, target in enumerate(transitions):
            validation = OmniMedhubOrderLifecycleEngine.validate_transition(current, target)
            if not validation.is_ok():
                return Err(Exception(
                    f"Transition failed at step {i + 1}: {validation.unwrap_err()}"
                ))
            audit_trail.append({
                "step": i + 1,
                "from": current,
                "to": target,
                "action": f"{current} → {target}",
            })
            current = target

        return Ok({
            "final_state": current,
            "audit_trail": audit_trail,
            "transition_count": len(transitions),
        })

    @staticmethod
    def get_reachable_states(current_state: str) -> Result:
        """Get all states reachable from the current state (BFS).

        Args:
            current_state: The current order state.

        Returns:
            Result[list[str], Exception]: Sorted list of all reachable states.
        """
        if current_state not in OmniMedhubOrderLifecycleEngine.ALL_STATES:
            return Err(Exception(f"Unknown state: '{current_state}'"))

        visited: set[str] = set()
        queue = [current_state]

        while queue:
            state = queue.pop(0)
            if state in visited:
                continue
            visited.add(state)
            for next_state in OmniMedhubOrderLifecycleEngine.TRANSITION_TABLE.get(state, set()):
                if next_state not in visited:
                    queue.append(next_state)

        visited.discard(current_state)
        return Ok(sorted(visited))
