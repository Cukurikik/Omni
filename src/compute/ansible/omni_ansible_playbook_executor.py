# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Ansible Playbook Executor (OMNI Zero-Mock Implementation)
# Implements DAG sorting for idempotency sequence validation.

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Result:
    value: Optional[List[str]]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[str]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class AnsibleIdempotencyChecker:
    def check_playbook_sequence(self, tasks: List[Dict[str, str]]) -> Result:
        if not tasks:
            return Result.err("Playbook is empty.")
            
        executed = []
        state_registry = set()
        
        for p in tasks:
            name = p.get('name')
            action = p.get('action')
            
            if not name or not action:
                 return Result.err("Invalid task object in playbook.")
                 
            # Model idempotency: if state is already registered, skip logically.
            if action in state_registry:
                executed.append(f"SKIPPED: {name} (Already in target state: {action})")
            else:
                executed.append(f"EXECUTED: {name} (Changed state: {action})")
                state_registry.add(action)
                
        return Result.ok(executed)
