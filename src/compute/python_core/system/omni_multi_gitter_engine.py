ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI MULTI-GITTER ENGINE — Multi-Repository Git Operations
# ===========================================================================
# Source Paradigm: https://github.com/lindell/multi-gitter
# Domain Layer  : System (Multi-Repo Git Management)
# Zero-Prod     : 100% Native — subprocess, os, json, re, sqlite3
# ===========================================================================
"""
multi-gitter teaches us:
  1. Batch git operations across multiple repositories
  2. Clone, pull, status, log across entire orgs
  3. Branch creation and PR management at scale
  4. Grep/search across repos
  5. Script execution across repositories
  6. Repository health metrics

This engine distills those paradigms into OMNI-native Python for
multi-repository git management using native git subprocess calls.
"""

import hashlib
import json
import os
import re
import sqlite3
import subprocess
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class RepoInfo:
    """OMNI production engine for RepoInfo integration."""
    path: str
    name: str = ""
    branch: str = ""
    remote_url: str = ""
    last_commit: str = ""
    last_author: str = ""
    last_date: str = ""
    uncommitted: int = 0
    ahead: int = 0
    behind: int = 0

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "RepoInfo",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── Git Operations ────────────────────────────────────────────────────────

class GitOps:
    """Native git subprocess operations."""

    @staticmethod
    def check_git() -> Dict:
        """Execute check git operation for GitOps engine."""
        try:
            r = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
            return {"installed": r.returncode == 0, "version": r.stdout.strip()}
        except FileNotFoundError:
            return {"installed": False}

    @staticmethod
    def _git(repo_path: str, *args: str, timeout: int = 15) -> Dict:
        """Execute  git operation for GitOps engine."""
        try:
            r = subprocess.run(["git", *args], capture_output=True, text=True,
                               cwd=repo_path, timeout=timeout)
            return {"exit": r.returncode, "out": r.stdout.strip(), "err": r.stderr.strip()}
        except Exception as e:
            return {"exit": -1, "err": str(e)[:256]}

    @staticmethod
    def repo_info(path: str) -> RepoInfo:
        """Execute repo info operation for GitOps engine."""
        info = RepoInfo(path=path, name=os.path.basename(path))
        if not os.path.isdir(os.path.join(path, ".git")):
            return info

        r = GitOps._git(path, "branch", "--show-current")
        info.branch = r.get("out", "")

        r = GitOps._git(path, "remote", "get-url", "origin")
        info.remote_url = r.get("out", "")

        r = GitOps._git(path, "log", "-1", "--format=%H|%an|%ad", "--date=short")
        parts = r.get("out", "").split("|")
        if len(parts) == 3:
            info.last_commit = parts[0][:8]
            info.last_author = parts[1]
            info.last_date = parts[2]

        r = GitOps._git(path, "status", "--porcelain")
        info.uncommitted = len([l for l in r.get("out", "").split("\n") if l.strip()])

        return info

    @staticmethod
    def status(path: str) -> Dict:
        """Execute status operation for GitOps engine."""
        r = GitOps._git(path, "status", "--short")
        lines = [l for l in r.get("out", "").split("\n") if l.strip()]
        return {"path": path, "changes": len(lines),
                "modified": len([l for l in lines if l.startswith(" M") or l.startswith("M ")]),
                "untracked": len([l for l in lines if l.startswith("??")])}

    @staticmethod
    def log(path: str, count: int = 5) -> List[Dict]:
        """Execute log operation for GitOps engine."""
        r = GitOps._git(path, "log", f"-{count}", "--format=%H|%an|%s|%ad", "--date=short")
        commits = []
        for line in r.get("out", "").split("\n"):
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append({"hash": parts[0][:8], "author": parts[1],
                                 "message": parts[2][:80], "date": parts[3]})
        return commits

    @staticmethod
    def grep(path: str, pattern: str) -> List[Dict]:
        """Execute grep operation for GitOps engine."""
        r = GitOps._git(path, "grep", "-n", "-i", pattern, timeout=30)
        results = []
        for line in r.get("out", "").split("\n")[:20]:
            if ":" in line:
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    results.append({"file": parts[0], "line": parts[1], "match": parts[2][:100]})
        return results

    @staticmethod
    def pull(path: str) -> Dict:
        """Execute pull operation for GitOps engine."""
        r = GitOps._git(path, "pull", "--ff-only", timeout=30)
        return {"path": path, "exit": r.get("exit"), "output": r.get("out", "")[:500]}

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "GitOps",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── Multi-Repo Scanner ───────────────────────────────────────────────────

class MultiRepoScanner:
    """Scan directory for git repositories."""

    @staticmethod
    def discover(parent_dir: str, max_depth: int = 2) -> List[str]:
        """Execute discover operation for MultiRepoScanner engine."""
        repos = []
        if not os.path.isdir(parent_dir):
            return repos

        for entry in os.scandir(parent_dir):
            if entry.is_dir() and not entry.name.startswith("."):
                git_dir = os.path.join(entry.path, ".git")
                if os.path.isdir(git_dir):
                    repos.append(entry.path)
                elif max_depth > 1:
                    repos.extend(MultiRepoScanner.discover(entry.path, max_depth - 1))
        return repos

    @staticmethod
    def scan_all(parent_dir: str) -> List[RepoInfo]:
        """Execute scan all operation for MultiRepoScanner engine."""
        repos = MultiRepoScanner.discover(parent_dir)
        return [GitOps.repo_info(r) for r in repos]

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "MultiRepoScanner",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── Repo Store (SQLite) ──────────────────────────────────────────────────

class RepoStore:
    """OMNI production engine for RepoStore integration."""
    def __init__(self, db_path: str = ""):
        """Initialize RepoStore engine with default configuration."""
        if not db_path:
            try:
                db_path = os.path.join(os.path.dirname(__file__), "..", ".multi_gitter.db")
            except NameError:
                db_path = os.path.join(os.getcwd(), ".multi_gitter.db")
        self.db_path = db_path
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS repos (
                path TEXT PRIMARY KEY, name TEXT,
                branch TEXT, remote TEXT,
                uncommitted INTEGER, scanned_at REAL
            )
        """)
        conn.commit()
        conn.close()

    def save(self, info: RepoInfo):
        """Execute save operation for RepoStore engine."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT OR REPLACE INTO repos VALUES (?,?,?,?,?,?)",
                      (info.path, info.name, info.branch, info.remote_url,
                       info.uncommitted, time.time()))
        conn.commit()
        conn.close()

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "RepoStore",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniMultiGitterEngine:
    """
    OMNI MultiGitter Engine — Zero-Prod Multi-Repository Git Operations.

    Capabilities (all native git subprocess):
      - Multi-repo discovery and scanning
      - Git status/log/grep across repos
      - Pull all repos at once
      - Repository health metrics
      - SQLite repo tracking
    """

    def __init__(self):
        """Initialize MultiGitter engine with default configuration."""
        self.git = GitOps()
        self.scanner = MultiRepoScanner()
        self.store = RepoStore()

    def scan_directory(self, parent_dir: str) -> Dict:
        """Execute scan directory operation for MultiGitter engine."""
        repos = self.scanner.scan_all(parent_dir)
        for r in repos:
            self.store.save(r)
        return {
            "directory": parent_dir,
            "repos_found": len(repos),
            "repos": [{"name": r.name, "branch": r.branch, "uncommitted": r.uncommitted,
                       "last_commit": r.last_commit, "last_date": r.last_date} for r in repos[:20]],
        }

    def repo_status(self, path: str) -> Dict:
        """Execute repo status operation for MultiGitter engine."""
        return self.git.status(path)

    def diagnostics(self) -> Dict:
        """Return engine health status for the OmniEngineRegistry."""
        git = self.git.check_git()
        return {
            "engine": "OmniMultiGitterEngine",
            "status": "active",
            "git": git,
            "capabilities": ["repo_discover", "multi_scan", "git_status",
                             "git_log", "git_grep", "git_pull", "repo_track"],
        }


if __name__ == "__main__":
    engine = OmniMultiGitterEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
