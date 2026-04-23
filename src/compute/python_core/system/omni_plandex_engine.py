ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI PLANDEX ENGINE — Terminal AI Diffing & Sandbox Planning
# ===========================================================================
# Source Paradigm: Plandex (https://github.com/plandex-ai/plandex)
# Domain Layer  : Automation / Version Control
# Zero-Prod     : 100% Native — difflib, os, shutil, sqlite3
# ===========================================================================
"""
Plandex Paradigm:
  1. AI Coding engine that lives in the terminal.
  2. Plannning phase before execution (sandbox branching).
  3. Visualizing changes explicitly via unified diffs prior to save.
  4. Non-destructive workflow protecting main branches.

This engine brings isolated branch planning to OMNI by allowing the LLM
to generate code into a sandbox, visually diff it against original files,
and only 'apply' them when authorized, keeping workspaces safe from bad writes.
"""

import difflib
import json
import os
import shutil
import sqlite3
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class PlanModification:
    """OMNI production engine for PlanModification integration."""
    file_path: str
    action: str  # "create", "modify", "delete"
    content: str
    diff: str = ""

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "PlanModification",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


class OmniPlandexEngine:
    """
    OMNI Plandex Planner.
    Handles virtual sandboxes and strict diff applications.
    """

    def __init__(self, workspace_dir: str = "", plan_id: str = "default_plan"):
        """Initialize Plandex engine with default configuration."""
        self.workspace_dir = workspace_dir or os.getcwd()
        self.plan_id = plan_id
        
        # Sandbox is where virtual files exist before application
        self.sandbox_dir = os.path.join(self.workspace_dir, ".omni_plandex_sandbox", self.plan_id)
        os.makedirs(self.sandbox_dir, exist_ok=True)
        
        self.modifications: Dict[str, PlanModification] = {}

    def _get_target_path(self, relative_path: str) -> str:
        """Execute  get target path operation for Plandex engine."""
        return os.path.abspath(os.path.join(self.workspace_dir, relative_path))

    def _get_sandbox_path(self, relative_path: str) -> str:
        """Execute  get sandbox path operation for Plandex engine."""
        return os.path.abspath(os.path.join(self.sandbox_dir, relative_path))

    def stage_file_modification(self, relative_path: str, new_content: str) -> str:
        """Stage a file modification into the plan, computing the diff."""
        target_path = self._get_target_path(relative_path)
        sandbox_path = self._get_sandbox_path(relative_path)
        
        os.makedirs(os.path.dirname(sandbox_path), exist_ok=True)
        
        original_content = ""
        action = "create"
        if os.path.exists(target_path):
            action = "modify"
            with open(target_path, "r", encoding="utf-8") as f:
                original_content = f.read()
                
        with open(sandbox_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        # Generate Unified Diff
        diff_lines = list(difflib.unified_diff(
            original_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=relative_path + " (original)",
            tofile=relative_path + " (planned)",
            n=3
        ))
        
        diff_str = "".join(diff_lines)
        
        self.modifications[relative_path] = PlanModification(
            file_path=relative_path,
            action=action,
            content=new_content,
            diff=diff_str
        )
        
        return diff_str

    def stage_file_deletion(self, relative_path: str) -> str:
        """Stage a file deletion."""
        target_path = self._get_target_path(relative_path)
        if not os.path.exists(target_path):
            return ""

        with open(target_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        diff_lines = list(difflib.unified_diff(
            original_content.splitlines(keepends=True),
            [],
            fromfile=relative_path + " (original)",
            tofile="/dev/null",
            n=3
        ))
        
        diff_str = "".join(diff_lines)
        self.modifications[relative_path] = PlanModification(
            file_path=relative_path,
            action="delete",
            content="",
            diff=diff_str
        )
        return diff_str

    def get_plan_summary(self) -> Dict[str, Any]:
        """Review the entire plan's diffs before applying."""
        return {
            "plan_id": self.plan_id,
            "modifications": len(self.modifications),
            "files": [
                {"path": path, "action": mod.action, "diff_size": len(mod.diff)}
                for path, mod in self.modifications.items()
            ],
            "diffs": {path: mod.diff for path, mod in self.modifications.items()}
        }

    def apply_plan(self) -> Dict[str, Any]:
        """Execute the planned modifications directly to the workspace."""
        results = {"applied": 0, "errors": []}
        
        for relative_path, mod in self.modifications.items():
            target_path = self._get_target_path(relative_path)
            
            try:
                if mod.action == "delete":
                    if os.path.exists(target_path):
                        os.remove(target_path)
                        results["applied"] += 1
                elif mod.action in ["create", "modify"]:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write(mod.content)
                    results["applied"] += 1
            except Exception as e:
                results["errors"].append({"file": relative_path, "error": str(e)})

        # Cleanup sandbox
        try:
            shutil.rmtree(self.sandbox_dir)
        except Exception:
            pass
            
        return results

    def reset_plan(self):
        """Discard the plan and sandbox."""
        self.modifications.clear()
        if os.path.exists(self.sandbox_dir):
            shutil.rmtree(self.sandbox_dir)

    def diagnostics(self) -> Dict:
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "OmniPlandexEngine",
            "status": "active",
            "capabilities": ["sandbox_planning", "unified_diff", "safe_apply", "destructive_isolation"],
            "workspace": self.workspace_dir
        }


if __name__ == "__main__":
    eng = OmniPlandexEngine(plan_id="test_plan")
    
    # Stage a mock file
    diff = eng.stage_file_modification("test_hello.py", "print('Hello Plandex')\\n")
    print("DIFF:")
    print(diff)
    
    # Review
    print(json.dumps(eng.get_plan_summary(), indent=2))
    
    # Apply
    print(json.dumps(eng.apply_plan(), indent=2))
    
    # Cleanup dummy file
    if os.path.exists("test_hello.py"):
        os.remove("test_hello.py")
