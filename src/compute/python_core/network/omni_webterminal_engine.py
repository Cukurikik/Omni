ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI WEBTERMINAL ENGINE — Web-Based SSH Terminal & Remote Shell
# ===========================================================================
# Source Paradigm: https://github.com/jimmy201602/webterminal
# Domain Layer  : Network (Web Terminal / SSH)
# Zero-Mock     : 100% Native — subprocess, socket, os, json, sqlite3
# ===========================================================================
"""
Webterminal teaches us:
  1. Web-based SSH terminal (WebSocket → PTY bridge)
  2. Session management with recording/replay
  3. Multi-protocol support (SSH, Telnet, SFTP)
  4. Command audit logging
  5. File transfer via SFTP
  6. Session sharing and collaboration

This engine distills those paradigms into OMNI-native Python for
local shell execution, SSH connectivity, and command audit logging.
"""

import hashlib
import json
import os
import socket
import sqlite3
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# ── Data Models ──────────────────────────────────────────────────────────────

class SessionStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    ERROR = "error"


@dataclass
class ShellSession:
    session_id: str
    session_type: str = "local"   # "local", "ssh"
    host: str = "localhost"
    user: str = ""
    status: SessionStatus = SessionStatus.ACTIVE
    commands_executed: int = 0
    created_at: float = 0
    closed_at: float = 0


@dataclass
class CommandResult:
    command: str
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    duration_ms: float = 0
    timestamp: float = 0


# ── Local Shell Executor ──────────────────────────────────────────────────

class LocalShell:
    """Execute commands in the local shell."""

    @staticmethod
    def execute(command: str, timeout: int = 30, cwd: str = None) -> CommandResult:
        start = time.perf_counter()
        result = CommandResult(command=command, timestamp=time.time())
        try:
            r = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=timeout, cwd=cwd,
            )
            result.exit_code = r.returncode
            result.stdout = r.stdout[:8192]
            result.stderr = r.stderr[:4096]
        except subprocess.TimeoutExpired:
            result.exit_code = -1
            result.stderr = f"Timeout ({timeout}s)"
        except Exception as e:
            result.exit_code = -1
            result.stderr = str(e)[:256]
        result.duration_ms = round((time.perf_counter() - start) * 1000, 2)
        return result

    @staticmethod
    def get_shell_info() -> Dict:
        info = {
            "os": os.name,
            "platform": os.sys.platform if hasattr(os, 'sys') else "",
            "cwd": os.getcwd(),
            "user": os.environ.get("USERNAME", os.environ.get("USER", "")),
            "home": os.path.expanduser("~"),
            "path_dirs": len(os.environ.get("PATH", "").split(os.pathsep)),
        }
        # Shell version
        if os.name == "nt":
            r = subprocess.run(["powershell", "-Command", "$PSVersionTable.PSVersion.ToString()"],
                               capture_output=True, text=True, timeout=5)
            info["shell"] = f"PowerShell {r.stdout.strip()}" if r.returncode == 0 else "PowerShell"
        else:
            r = subprocess.run(["bash", "--version"], capture_output=True, text=True, timeout=3)
            info["shell"] = r.stdout.split("\n")[0] if r.returncode == 0 else "bash"
        return info


# ── SSH Connector ──────────────────────────────────────────────────────────

class SSHConnector:
    """Test SSH connectivity and execute remote commands."""

    @staticmethod
    def test_connection(host: str, port: int = 22, timeout: float = 5) -> Dict:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                start = time.perf_counter()
                result = s.connect_ex((host, port))
                latency = round((time.perf_counter() - start) * 1000, 2)
                banner = ""
                if result == 0:
                    try:
                        s.settimeout(3)
                        banner = s.recv(256).decode("utf-8", errors="replace").strip()
                    except Exception:
                        pass
                return {"host": host, "port": port, "reachable": result == 0,
                        "latency_ms": latency, "banner": banner}
        except Exception as e:
            return {"host": host, "error": str(e)[:128]}

    @staticmethod
    def execute_remote(host: str, command: str, user: str = "", timeout: int = 15) -> Dict:
        target = f"{user}@{host}" if user else host
        try:
            r = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no",
                 "-o", "BatchMode=yes", target, command],
                capture_output=True, text=True, timeout=timeout,
            )
            return {"target": target, "exit_code": r.returncode,
                    "stdout": r.stdout[:4096], "stderr": r.stderr[:2048]}
        except FileNotFoundError:
            return {"error": "ssh not found"}
        except subprocess.TimeoutExpired:
            return {"error": "timeout"}
        except Exception as e:
            return {"error": str(e)[:256]}


# ── Command Audit Log (SQLite) ────────────────────────────────────────────

class CommandAudit:
    def __init__(self, db_path: str = ""):
        if not db_path:
            try:
                db_path = os.path.join(os.path.dirname(__file__), "..", ".webterminal_audit.db")
            except NameError:
                db_path = os.path.join(os.getcwd(), ".webterminal_audit.db")
        self.db_path = db_path
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT, command TEXT,
                exit_code INTEGER, duration_ms REAL,
                timestamp REAL
            )
        """)
        conn.commit()
        conn.close()

    def log(self, session_id: str, result: CommandResult):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO commands (session_id,command,exit_code,duration_ms,timestamp) VALUES (?,?,?,?,?)",
            (session_id, result.command[:500], result.exit_code, result.duration_ms, result.timestamp),
        )
        conn.commit()
        conn.close()

    def stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM commands")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM commands WHERE exit_code=0")
        success = c.fetchone()[0]
        conn.close()
        return {"total_commands": total, "successful": success, "failed": total - success}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniWebterminalEngine:
    """
    OMNI Webterminal Engine — Zero-Mock Web Terminal & Shell Management.

    Capabilities (all native subprocess + socket):
      - Local shell execution with timeout
      - SSH connectivity testing with banner grab
      - Remote command execution via SSH
      - Command audit logging (SQLite)
      - Shell environment inspection
    """

    def __init__(self):
        self.shell = LocalShell()
        self.ssh = SSHConnector()
        self.audit = CommandAudit()
        self._session_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:12]

    def execute(self, command: str, cwd: str = None) -> Dict:
        result = self.shell.execute(command, cwd=cwd)
        self.audit.log(self._session_id, result)
        return {
            "command": result.command, "exit_code": result.exit_code,
            "stdout": result.stdout[:2048], "stderr": result.stderr[:1024],
            "duration_ms": result.duration_ms,
        }

    def diagnostics(self) -> Dict:
        info = self.shell.get_shell_info()
        return {
            "engine": "OmniWebterminalEngine",
            "status": "active",
            "shell": info,
            "audit": self.audit.stats(),
            "capabilities": ["local_exec", "ssh_test", "ssh_exec",
                             "command_audit", "shell_info", "session_mgmt"],
        }


if __name__ == "__main__":
    engine = OmniWebterminalEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
