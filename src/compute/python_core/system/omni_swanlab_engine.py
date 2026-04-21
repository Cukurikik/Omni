import os
import json
from typing import Dict, Any

class OmniSwanLabEngine:
    """
    OMNI Engine for SwanLab AI Experiment Tracking.
    Tracks metrics, losses, and configurations for ML tasks.
    Source: https://github.com/SwanHubX/SwanLab.git
    """
    def __init__(self, workspace_dir: str = "", project_name: str = "omni_ai_project"):
        """Initialize SwanLab engine with default configuration."""
        self.workspace_dir = workspace_dir or os.getcwd()
        self.project_name = project_name
        self.log_dir = os.path.join(self.workspace_dir, "swanlog")
        self._is_tracking = False

    def init_experiment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Initializes a new SwanLab experiment."""
        try:
            import swanlab
            swanlab.init(
                project=self.project_name,
                workspace=self.workspace_dir,
                config=config,
                logdir=self.log_dir
            )
            self._is_tracking = True
            return {"status": "success", "message": f"Started SwanLab project: {self.project_name}"}
        except ImportError:
            return {"status": "error", "message": "swanlab package not installed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def log_metrics(self, metrics: Dict[str, float], step: int) -> Dict[str, Any]:
        """Logs scalar metrics to SwanLab."""
        if not self._is_tracking:
            return {"status": "error", "message": "Call init_experiment before logging."}
        try:
            import swanlab
            swanlab.log(metrics, step=step)
            return {"status": "success", "logged": metrics, "step": step}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def finish_experiment(self) -> Dict[str, Any]:
        """Finalizes and closes the SwanLab experiment log."""
        if not self._is_tracking:
            return {"status": "success", "message": "No active experiment to finish."}
        try:
            import swanlab
            swanlab.finish()
            self._is_tracking = False
            return {"status": "success", "message": "Experiment finished successfully."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "OmniSwanLabEngine",
            "project": self.project_name,
            "tracking": self._is_tracking,
            "log_dir": self.log_dir
        }
