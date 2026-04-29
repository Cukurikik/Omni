# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Apache Airflow (OMNI Zero-Mock Implementation)
# Implements DAG execution state polling dependencies verification.

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Result:
    value: Optional[List[str]] # Tasks that can now be scheduled
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[str]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class AirflowDAGExecutor:
    def get_schedulable_tasks(
        self, 
        dag: Dict[str, List[str]], 
        task_states: Dict[str, str]
    ) -> Result:
        """
        dag: { task_id : [upstream_dependency_task_ids] }
        states: "SUCCESS", "FAILED", "RUNNING", "NONE"
        """
        if not dag:
             return Result.err("DAG definition cannot be empty.")
             
        schedulable = []
        for task_id, upstreams in dag.items():
            if task_id not in task_states:
                 task_states[task_id] = "NONE"
                 
            # Only consider tasks that haven't run
            if task_states[task_id] == "NONE":
                 can_run = True
                 for dep in upstreams:
                     if dep not in task_states:
                          return Result.err(f"Unknown upstream dependency {dep} for {task_id}.")
                     if task_states[dep] != "SUCCESS":
                          can_run = False
                          break
                 if can_run:
                     schedulable.append(task_id)
                     
        return Result.ok(schedulable)
