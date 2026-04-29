import subprocess
import os
from typing import Tuple, Optional, Dict

# OMNI Ploomber - Task Runner Isolation
# Monadic task execution within isolated subprocess environments

class IsolatedTaskRunner:
    def __init__(self, executable: str = "python"):
        self.executable = executable

    def execute_script(self, script_path: str, env_vars: Optional[Dict[str, str]] = None) -> Tuple[bool, Optional[str], Optional[Exception]]:
        if not os.path.exists(script_path):
            return False, None, FileNotFoundError(f"Script not found: {script_path}")

        current_env = os.environ.copy()
        if env_vars:
            current_env.update(env_vars)

        try:
            result = subprocess.run(
                [self.executable, script_path],
                env=current_env,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                return True, result.stdout, None
            else:
                return False, result.stderr, RuntimeError(f"Task failed with exit code {result.returncode}")
                
        except Exception as e:
            return False, None, e
