"""
+============================================================================+
|  OMNI MAC DEV ENGINE                                                       |
|  Meta-functionalized from: geerlingguy/mac-dev-playbook                    |
|  Domain Layer: System                                                      |
|  Purpose: Hard-coded production execution of real macOS system commands.   |
|  Constraints: ZERO MOCKS. Real subprocess tracking.                        |
|  License: OMNI-Enterprise                                                  |
+============================================================================+
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import subprocess
import os
import platform

T = Any
E = Exception

@dataclass
class Result:
    """OMNI production engine for Result integration."""
    is_ok: bool
    value: Optional[T] = None
    error: Optional[E] = None

    @staticmethod
    def Ok(value: T) -> 'Result':
        """Execute Ok operation for Result engine."""
        return Result(is_ok=True, value=value)

    @staticmethod
    def Err(error: E) -> 'Result':
        """Execute Err operation for Result engine."""
        return Result(is_ok=False, error=error)

    def unwrap(self) -> T:
        """Execute unwrap operation for Result engine."""
        if not self.is_ok:
            raise self.error or Exception("Unwrapped an Err result")
        return self.value

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "Result",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }

class OmniMacDevEngine:
    """
    Executes actual bash scripts and system state changes for macOS development.
    Uses real subprocess execution. Rejects execution on Windows/Linux.
    """
    
    ENGINE_VERSION = "2.0.0-PROD"

    def __init__(self):
        """Initialize MacDev engine with default configuration."""
        self.os_type = platform.system()

    def _execute_real_command(self, cmd_args: List[str]) -> Result:
        """Internal: Safely runs a real OS command returning stdout as Result."""
        if self.os_type != "Darwin":
            return Result.Err(Exception(f"Unsupported OS: {self.os_type}. MacDevEngine requires Darwin."))
            
        try:
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return Result.Ok({"stdout": result.stdout.strip()})
            else:
                return Result.Err(Exception(f"Command failed (Return {result.returncode}): {result.stderr.strip()}"))
        except Exception as e:
            return Result.Err(e)

    def install_homebrew_package(self, package_name: str) -> Result:
        """Executes a real `brew install` command."""
        return self._execute_real_command(["brew", "install", package_name])

    def configure_macos_default(self, domain: str, key: str, val_type: str, value: str) -> Result:
        """
        Executes a real `defaults write` command.
        Example: set_macos_default("-g", "InitialKeyRepeat", "-int", "10")
        """
        return self._execute_real_command(["defaults", "write", domain, key, val_type, value])

    def check_system_info(self) -> Result:
        """Executes a real `system_profiler` hardware lookup."""
        return self._execute_real_command(["system_profiler", "SPSoftwareDataType"])

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Framework standard diagnostics method."""
        return {
            "engine": "OmniMacDevEngine",
            "version": self.ENGINE_VERSION,
            "os_type": self.os_type,
            "is_operable": self.os_type == "Darwin"
        }

# ============================================================================
# Engine Self-Test
# ============================================================================
def _run_self_test():
    engine = OmniMacDevEngine()
    
    if engine.os_type == "Darwin":
        # Safe read-only test on Mac
        res = engine.check_system_info()
        assert res.is_ok
    else:
        # Proper failure on Windows/Linux
        res = engine.check_system_info()
        assert not res.is_ok
        assert "Unsupported OS" in str(res.error)
    
    diag = engine.diagnostics()
    assert diag["engine"] == "OmniMacDevEngine"
    print("OmniMacDevEngine: Production unmocked tests passed.")

if __name__ == "__main__":
    _run_self_test()
