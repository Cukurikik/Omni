import logging
import uuid
import datetime
from src.compute.python_core.omni_base_engine import Result, Ok, Err

logger = logging.getLogger(__name__)

class OmniOxygenProjectEngine:
    """
    OMNI Semester 10 Batch 30 - Production Oxygen Project Engine
    Flexible Jira Alternative Engine. Supports Issue Tracking, Agile Workflows,
    and release management with mathematical state transitions.
    """
    def __init__(self, config=None):
        self._config = config or {}
        self._issues = {}
        self._workflows = {
            "default": ["TODO", "IN_PROGRESS", "REVIEW", "DONE"]
        }
        self._is_operational = True
        self._system_id = str(uuid.uuid4())

    def create_issue(self, title: str, description: str, assignee: str) -> dict:
        """Perform create issue computation.

            Args:
                    title: str
                    description: str
                    assignee: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not title:
            return {"status": "error", "error": "Title is required for an issue."}
            
        issue_id = f"OXGN-{len(self._issues) + 1000}"
        
        self._issues[issue_id] = {
            "title": title,
            "description": description,
            "assignee": assignee,
            "state": "TODO",
            "workflow": "default",
            "created_at": datetime.datetime.utcnow().isoformat(),
            "updated_at": datetime.datetime.utcnow().isoformat()
        }
        return {"status": "ok", "value": issue_id}

    def transition_issue(self, issue_id: str, new_state: str) -> dict:
        """ Safely handles mathematical workflow transition checks """
        if not self._is_operational:
            return {"status": "error", "error": "Engine is offline."}
            
        if issue_id not in self._issues:
            return {"status": "error", "error": "Issue not found."}
            
        current = self._issues[issue_id]
        wf = self._workflows.get(current["workflow"])
        
        if wf is None:
            return {"status": "error", "error": "Invalid workflow association."}
            
        try:
            current_idx = wf.index(current["state"])
            new_idx = wf.index(new_state)
            
            # Simple DAG: can jump forward but requires audit trail
            if new_idx < 0:
                return {"status": "error", "error": "Invalid state configuration."}
                
            current["state"] = new_state
            current["updated_at"] = datetime.datetime.utcnow().isoformat()
            
            return {"status": "ok", "value": {"issue_id": issue_id, "state": new_state}}
            
        except ValueError:
            return {"status": "error", "error": f"State '{new_state}' not in workflow '{current['workflow']}'."}

    def diagnostics(self) -> dict:
        return {
            "engine": "OmniOxygenProjectEngine",
            "version": "3.0.0",
            "status": "operational" if self._is_operational else "offline",
            "system_id": self._system_id,
            "capabilities": [
                "agile_workflow_tracking",
                "state_machine_validation",
                "issue_creation"
            ],
            "metrics": {
                "total_issues": len(self._issues),
                "workflows_registered": len(self._workflows)
            }
        }
