ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI N8N ENGINE — Visual Workflow Automation & Node Orchestration
# ===========================================================================
# Source Paradigm: https://github.com/n8n-io/n8n
# Domain Layer  : Network (Workflow Automation)
# Zero-Mock     : 100% Native — json, os, time, hashlib, sqlite3, urllib
# ===========================================================================
"""
n8n teaches us:
  1. Visual workflow builder with connected nodes
  2. Trigger-based execution (webhook, schedule, manual)
  3. Node types: HTTP Request, Transform, Filter, Merge, Switch
  4. Data flow between nodes via input/output connections
  5. Error handling with try/catch nodes
  6. Credential management for external services
  7. Workflow templates and sharing

This engine distills those paradigms into OMNI-native Python for
workflow definition, node execution, and pipeline orchestration.
"""

import hashlib
import json
import os
import re
import sqlite3
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


# ── Data Models ──────────────────────────────────────────────────────────────

class NodeType(Enum):
    TRIGGER_MANUAL = "trigger_manual"
    TRIGGER_WEBHOOK = "trigger_webhook"
    TRIGGER_SCHEDULE = "trigger_schedule"
    HTTP_REQUEST = "http_request"
    SET = "set"                      # Set/transform data
    IF = "if"                        # Conditional branch
    SWITCH = "switch"                # Multi-branch
    MERGE = "merge"                  # Merge inputs
    FILTER = "filter"                # Filter items
    CODE = "code"                    # Custom Python code
    SPLIT = "split"                  # Split array into items
    AGGREGATE = "aggregate"          # Aggregate items
    RESPOND = "respond"              # Return response
    NO_OP = "no_op"                  # Pass-through


class WorkflowStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class WorkflowNode:
    node_id: str
    name: str
    node_type: NodeType
    parameters: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0})
    connections_out: List[str] = field(default_factory=list)  # node_ids
    retry_on_fail: bool = False
    max_retries: int = 0
    continue_on_fail: bool = False


@dataclass
class NodeExecution:
    node_id: str
    name: str
    status: str = "pending"
    input_data: Any = None
    output_data: Any = None
    duration_ms: float = 0
    error: str = ""


@dataclass
class Workflow:
    workflow_id: str
    name: str
    nodes: Dict[str, WorkflowNode] = field(default_factory=dict)
    trigger_node_id: str = ""
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: float = 0
    last_run: float = 0
    run_count: int = 0
    tags: List[str] = field(default_factory=list)


# ── Node Executors ────────────────────────────────────────────────────────

class NodeExecutors:
    """Execute individual node types."""

    @staticmethod
    def execute_http_request(params: Dict, input_data: Any) -> Any:
        url = params.get("url", "")
        method = params.get("method", "GET").upper()
        headers = params.get("headers", {})
        body = params.get("body", "")

        # Variable substitution from input data
        if isinstance(input_data, dict):
            for k, v in input_data.items():
                url = url.replace(f"={{{{{k}}}}}", str(v))

        if "User-Agent" not in headers:
            headers["User-Agent"] = "OMNI-n8n/1.0"

        try:
            data = body.encode("utf-8") if body else None
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=30) as resp:
                response_body = resp.read().decode("utf-8", errors="replace")
                try:
                    return {"status": resp.getcode(), "data": json.loads(response_body)}
                except json.JSONDecodeError:
                    return {"status": resp.getcode(), "data": response_body[:5000]}
        except urllib.error.HTTPError as e:
            return {"status": e.code, "error": str(e)[:200]}
        except Exception as e:
            return {"error": str(e)[:200]}

    @staticmethod
    def execute_set(params: Dict, input_data: Any) -> Any:
        """Set/transform data — assign values."""
        values = params.get("values", {})
        result = dict(input_data) if isinstance(input_data, dict) else {}
        result.update(values)
        return result

    @staticmethod
    def execute_if(params: Dict, input_data: Any) -> Any:
        """Conditional — returns data if condition met, None otherwise."""
        field_name = params.get("field", "")
        operator = params.get("operator", "==")
        compare_value = params.get("value", "")

        if not isinstance(input_data, dict):
            return None

        actual = str(input_data.get(field_name, ""))
        compare = str(compare_value)

        conditions = {
            "==": actual == compare,
            "!=": actual != compare,
            "contains": compare in actual,
            "not_contains": compare not in actual,
            "exists": field_name in input_data,
            "not_empty": bool(actual),
            ">": float(actual or 0) > float(compare or 0),
            "<": float(actual or 0) < float(compare or 0),
        }
        passed = conditions.get(operator, False)
        return input_data if passed else None

    @staticmethod
    def execute_filter(params: Dict, input_data: Any) -> Any:
        """Filter items from a list."""
        field_name = params.get("field", "")
        operator = params.get("operator", "==")
        compare_value = params.get("value", "")

        if isinstance(input_data, list):
            result = []
            for item in input_data:
                if isinstance(item, dict):
                    actual = str(item.get(field_name, ""))
                    if operator == "==" and actual == str(compare_value):
                        result.append(item)
                    elif operator == "contains" and str(compare_value) in actual:
                        result.append(item)
                    elif operator == "!=" and actual != str(compare_value):
                        result.append(item)
            return result
        return input_data

    @staticmethod
    def execute_merge(params: Dict, input_data: Any) -> Any:
        """Merge multiple data sources."""
        if isinstance(input_data, list):
            merged = {}
            for item in input_data:
                if isinstance(item, dict):
                    merged.update(item)
            return merged
        return input_data

    @staticmethod
    def execute_code(params: Dict, input_data: Any) -> Any:
        """Execute custom expression (safe subset)."""
        expression = params.get("expression", "")
        if not expression:
            return input_data

        # Safe evaluation: only math and string operations
        context = {"data": input_data, "len": len, "str": str, "int": int,
                    "float": float, "round": round, "abs": abs, "max": max, "min": min}
        try:
            result = eval(expression, {"__builtins__": {}}, context)
            return result
        except Exception as e:
            return {"error": f"Code execution failed: {str(e)[:100]}"}

    @staticmethod
    def execute_split(params: Dict, input_data: Any) -> Any:
        """Split data by field."""
        field_name = params.get("field", "")
        if isinstance(input_data, dict) and field_name in input_data:
            val = input_data[field_name]
            if isinstance(val, list):
                return val
            if isinstance(val, str):
                delimiter = params.get("delimiter", ",")
                return val.split(delimiter)
        return [input_data] if not isinstance(input_data, list) else input_data

    @staticmethod
    def execute_aggregate(params: Dict, input_data: Any) -> Any:
        """Aggregate list into summary."""
        if isinstance(input_data, list):
            return {
                "count": len(input_data),
                "items": input_data[:100],
            }
        return {"count": 1, "items": [input_data]}


# ── Workflow Executor ─────────────────────────────────────────────────────

class WorkflowExecutor:
    """Execute entire workflows by traversing the node graph."""

    EXECUTORS = {
        NodeType.HTTP_REQUEST: NodeExecutors.execute_http_request,
        NodeType.SET: NodeExecutors.execute_set,
        NodeType.IF: NodeExecutors.execute_if,
        NodeType.FILTER: NodeExecutors.execute_filter,
        NodeType.MERGE: NodeExecutors.execute_merge,
        NodeType.CODE: NodeExecutors.execute_code,
        NodeType.SPLIT: NodeExecutors.execute_split,
        NodeType.AGGREGATE: NodeExecutors.execute_aggregate,
    }

    @staticmethod
    def execute(workflow: Workflow, trigger_data: Any = None) -> Dict:
        workflow.status = WorkflowStatus.RUNNING
        executions: List[NodeExecution] = []
        node_outputs: Dict[str, Any] = {}

        # Find trigger/start node
        start_id = workflow.trigger_node_id
        if not start_id and workflow.nodes:
            start_id = list(workflow.nodes.keys())[0]

        # BFS traversal
        queue = [start_id]
        visited = set()
        current_data = trigger_data or {}

        while queue:
            nid = queue.pop(0)
            if nid in visited or nid not in workflow.nodes:
                continue
            visited.add(nid)

            node = workflow.nodes[nid]
            ex = NodeExecution(node_id=nid, name=node.name, input_data=current_data)

            start = time.perf_counter()
            try:
                # Trigger nodes just pass data through
                if node.node_type in (NodeType.TRIGGER_MANUAL, NodeType.TRIGGER_WEBHOOK,
                                       NodeType.TRIGGER_SCHEDULE, NodeType.NO_OP,
                                       NodeType.RESPOND):
                    ex.output_data = current_data
                    ex.status = "success"
                else:
                    executor = WorkflowExecutor.EXECUTORS.get(node.node_type)
                    if executor:
                        result = executor(node.parameters, current_data)
                        ex.output_data = result
                        ex.status = "success" if result is not None else "skipped"
                    else:
                        ex.output_data = current_data
                        ex.status = "no_executor"
            except Exception as e:
                ex.error = str(e)[:200]
                ex.status = "failed"
                if not node.continue_on_fail:
                    ex.duration_ms = round((time.perf_counter() - start) * 1000, 2)
                    executions.append(ex)
                    break

            ex.duration_ms = round((time.perf_counter() - start) * 1000, 2)
            executions.append(ex)
            node_outputs[nid] = ex.output_data

            # Propagate output to connected nodes
            if ex.output_data is not None:
                current_data = ex.output_data
                queue.extend(node.connections_out)

        all_success = all(e.status in ("success", "no_executor") for e in executions)
        workflow.status = WorkflowStatus.COMPLETED if all_success else WorkflowStatus.FAILED
        workflow.run_count += 1
        workflow.last_run = time.time()

        return {
            "workflow": workflow.name,
            "status": workflow.status.value,
            "nodes_executed": len(executions),
            "executions": [{"node": e.name, "status": e.status,
                            "ms": e.duration_ms, "output_preview": str(e.output_data)[:200]}
                           for e in executions],
        }


# ── Workflow Builder ──────────────────────────────────────────────────────

class WorkflowBuilder:
    @staticmethod
    def create(name: str) -> Workflow:
        wid = hashlib.sha256(f"{name}{time.time()}".encode()).hexdigest()[:12]
        return Workflow(workflow_id=wid, name=name, created_at=time.time())

    @staticmethod
    def add_node(wf: Workflow, name: str, node_type: str,
                  params: Dict = None, connect_after: str = "") -> str:
        nid = hashlib.sha256(f"{name}{len(wf.nodes)}".encode()).hexdigest()[:8]
        try:
            nt = NodeType(node_type)
        except ValueError:
            nt = NodeType.NO_OP
        node = WorkflowNode(node_id=nid, name=name, node_type=nt,
                             parameters=params or {})
        wf.nodes[nid] = node
        if not wf.trigger_node_id:
            wf.trigger_node_id = nid
        if connect_after and connect_after in wf.nodes:
            wf.nodes[connect_after].connections_out.append(nid)
        return nid


# ── Workflow Store (SQLite) ──────────────────────────────────────────────

class WorkflowStore:
    def __init__(self, db_path: str = ""):
        if not db_path:
            try:
                db_path = os.path.join(os.path.dirname(__file__), "..", ".n8n_workflows.db")
            except NameError:
                db_path = os.path.join(os.getcwd(), ".n8n_workflows.db")
        self.db_path = db_path
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                workflow_id TEXT PRIMARY KEY, name TEXT,
                nodes INTEGER, status TEXT, runs INTEGER, created_at REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS run_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT, status TEXT,
                nodes_executed INTEGER, run_at REAL
            )
        """)
        conn.commit()
        conn.close()

    def save(self, wf: Workflow):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT OR REPLACE INTO workflows VALUES (?,?,?,?,?,?)",
                      (wf.workflow_id, wf.name, len(wf.nodes),
                       wf.status.value, wf.run_count, wf.created_at))
        conn.commit()
        conn.close()

    def log_run(self, wf_id: str, status: str, nodes: int):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO run_log (workflow_id,status,nodes_executed,run_at) VALUES (?,?,?,?)",
                      (wf_id, status, nodes, time.time()))
        conn.commit()
        conn.close()

    def stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM workflows")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM run_log")
        runs = c.fetchone()[0]
        conn.close()
        return {"workflows": total, "total_runs": runs}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniN8NEngine:
    """
    OMNI n8n Engine — Zero-Mock Visual Workflow Automation.

    Capabilities (all native stdlib):
      - Workflow builder with 14 node types
      - HTTP Request, Set, If, Filter, Merge, Code, Split, Aggregate nodes
      - Trigger types: manual, webhook, schedule
      - BFS graph traversal execution
      - Variable substitution between nodes
      - Workflow persistence and run logging (SQLite)
    """

    def __init__(self):
        self.builder = WorkflowBuilder()
        self.executor = WorkflowExecutor()
        self.store = WorkflowStore()

    def run_workflow(self, name: str, nodes: List[Dict],
                      trigger_data: Any = None) -> Dict:
        wf = self.builder.create(name)
        prev_id = ""
        for n in nodes:
            nid = self.builder.add_node(
                wf, n.get("name", "node"), n.get("type", "no_op"),
                n.get("params", {}), prev_id)
            prev_id = nid

        result = self.executor.execute(wf, trigger_data)
        self.store.save(wf)
        self.store.log_run(wf.workflow_id, result["status"], result["nodes_executed"])
        return result

    def diagnostics(self) -> Dict:
        return {
            "engine": "OmniN8NEngine",
            "status": "active",
            "node_types": [n.value for n in NodeType],
            "db": self.store.stats(),
            "capabilities": ["workflow_build", "node_graph", "http_request",
                             "conditional_if", "data_filter", "data_merge",
                             "code_exec", "split_aggregate", "var_substitute",
                             "bfs_traverse", "run_log", "workflow_persist"],
        }


if __name__ == "__main__":
    engine = OmniN8NEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
