ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI DYNAMO ENGINE — Visual Programming & Computational Design Graphs
# ===========================================================================
# Source Paradigm: https://github.com/DynamoDS/Dynamo
# Domain Layer  : Domain (Visual Programming / BIM)
# Zero-Mock     : 100% Native — json, os, hashlib, math, sqlite3
# ===========================================================================
"""
Dynamo teaches us:
  1. Node-based visual programming (input → transform → output)
  2. Directed Acyclic Graph (DAG) execution model
  3. Computational design workflows (geometry, math, data)
  4. Parametric modeling with sliders and code blocks
  5. Custom node authoring and package management
  6. BIM integration (Autodesk Revit, Civil 3D)

This engine distills those paradigms into OMNI-native Python for
node-graph definition, DAG execution, and parametric computation.
"""

import hashlib
import json
import math
import os
import sqlite3
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


# ── Data Models ──────────────────────────────────────────────────────────────

class NodeCategory(Enum):
    INPUT = "input"
    MATH = "math"
    STRING = "string"
    LIST = "list"
    GEOMETRY = "geometry"
    LOGIC = "logic"
    OUTPUT = "output"
    CUSTOM = "custom"


@dataclass
class Port:
    name: str
    port_type: str = "any"    # "number", "string", "list", "bool", "any"
    value: Any = None
    connected_to: str = ""    # "node_id.port_name"


@dataclass
class GraphNode:
    node_id: str
    name: str
    category: NodeCategory = NodeCategory.CUSTOM
    inputs: List[Port] = field(default_factory=list)
    outputs: List[Port] = field(default_factory=list)
    operation: str = ""       # built-in operation name
    code: str = ""            # custom code block
    position: Tuple[float, float] = (0, 0)
    computed: bool = False


@dataclass
class NodeGraph:
    graph_id: str
    name: str
    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    connections: List[Tuple[str, str, str, str]] = field(default_factory=list)
    # (src_node, src_port, dst_node, dst_port)
    variables: Dict[str, Any] = field(default_factory=dict)
    created_at: float = 0


# ── Built-in Operations ───────────────────────────────────────────────────

class BuiltinOps:
    """Library of built-in node operations."""

    @staticmethod
    def execute(op: str, inputs: Dict[str, Any]) -> Any:
        # Math
        if op == "add":
            return inputs.get("a", 0) + inputs.get("b", 0)
        elif op == "subtract":
            return inputs.get("a", 0) - inputs.get("b", 0)
        elif op == "multiply":
            return inputs.get("a", 0) * inputs.get("b", 0)
        elif op == "divide":
            b = inputs.get("b", 1)
            return inputs.get("a", 0) / b if b != 0 else 0
        elif op == "power":
            return inputs.get("a", 0) ** inputs.get("b", 2)
        elif op == "sqrt":
            return math.sqrt(max(0, inputs.get("a", 0)))
        elif op == "abs":
            return abs(inputs.get("a", 0))
        elif op == "sin":
            return math.sin(math.radians(inputs.get("a", 0)))
        elif op == "cos":
            return math.cos(math.radians(inputs.get("a", 0)))
        elif op == "round":
            return round(inputs.get("a", 0), int(inputs.get("decimals", 0)))
        elif op == "min":
            return min(inputs.get("a", 0), inputs.get("b", 0))
        elif op == "max":
            return max(inputs.get("a", 0), inputs.get("b", 0))
        elif op == "clamp":
            return max(inputs.get("min", 0), min(inputs.get("max", 1), inputs.get("a", 0)))

        # String
        elif op == "concat":
            return str(inputs.get("a", "")) + str(inputs.get("b", ""))
        elif op == "upper":
            return str(inputs.get("a", "")).upper()
        elif op == "lower":
            return str(inputs.get("a", "")).lower()
        elif op == "length":
            return len(inputs.get("a", ""))
        elif op == "replace":
            return str(inputs.get("a", "")).replace(
                str(inputs.get("old", "")), str(inputs.get("new", "")))

        # List
        elif op == "range":
            return list(range(int(inputs.get("start", 0)),
                              int(inputs.get("end", 10)),
                              int(inputs.get("step", 1))))
        elif op == "list_sum":
            return sum(inputs.get("list", []))
        elif op == "list_avg":
            lst = inputs.get("list", [])
            return sum(lst) / max(len(lst), 1)
        elif op == "list_sort":
            return sorted(inputs.get("list", []))
        elif op == "list_reverse":
            return list(reversed(inputs.get("list", [])))
        elif op == "list_filter":
            threshold = inputs.get("threshold", 0)
            return [x for x in inputs.get("list", []) if x > threshold]

        # Logic
        elif op == "if":
            return inputs.get("true_val") if inputs.get("condition") else inputs.get("false_val")
        elif op == "equal":
            return inputs.get("a") == inputs.get("b")
        elif op == "greater":
            return inputs.get("a", 0) > inputs.get("b", 0)
        elif op == "not":
            return not inputs.get("a", False)

        # Geometry (2D point operations)
        elif op == "point":
            return {"x": inputs.get("x", 0), "y": inputs.get("y", 0), "z": inputs.get("z", 0)}
        elif op == "distance":
            a = inputs.get("a", {"x": 0, "y": 0})
            b = inputs.get("b", {"x": 0, "y": 0})
            return math.sqrt((a["x"] - b["x"])**2 + (a["y"] - b["y"])**2)
        elif op == "midpoint":
            a = inputs.get("a", {"x": 0, "y": 0})
            b = inputs.get("b", {"x": 0, "y": 0})
            return {"x": (a["x"]+b["x"])/2, "y": (a["y"]+b["y"])/2}

        # Output
        elif op == "watch":
            return inputs.get("value")
        elif op == "to_string":
            return str(inputs.get("value", ""))

        return inputs


# ── DAG Executor ───────────────────────────────────────────────────────────

class DAGExecutor:
    """Execute node graphs in topological order."""

    @staticmethod
    def topological_sort(graph: NodeGraph) -> List[str]:
        """Sort nodes for execution order."""
        in_degree = {nid: 0 for nid in graph.nodes}
        for src, _, dst, _ in graph.connections:
            if dst in in_degree:
                in_degree[dst] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        order = []
        while queue:
            nid = queue.pop(0)
            order.append(nid)
            for src, _, dst, _ in graph.connections:
                if src == nid and dst in in_degree:
                    in_degree[dst] -= 1
                    if in_degree[dst] == 0:
                        queue.append(dst)
        return order

    @staticmethod
    def execute(graph: NodeGraph) -> Dict:
        """Execute the entire graph."""
        order = DAGExecutor.topological_sort(graph)
        results = {}
        node_outputs: Dict[str, Dict[str, Any]] = {}

        for nid in order:
            node = graph.nodes[nid]
            # Collect inputs
            inputs = {}
            for port in node.inputs:
                if port.connected_to:
                    parts = port.connected_to.split(".")
                    if len(parts) == 2 and parts[0] in node_outputs:
                        inputs[port.name] = node_outputs[parts[0]].get(parts[1], port.value)
                    else:
                        inputs[port.name] = port.value
                else:
                    inputs[port.name] = port.value

            # Execute
            try:
                if node.operation:
                    result = BuiltinOps.execute(node.operation, inputs)
                elif node.code:
                    result = eval(node.code, {"__builtins__": {"math": math}}, inputs)
                else:
                    result = inputs

                # Store outputs — for input nodes, use defined port values
                out = {}
                if node.outputs:
                    for p in node.outputs:
                        if p.value is not None and not node.operation and not node.code:
                            out[p.name] = p.value  # input node: use port value
                        else:
                            out[p.name] = result
                else:
                    out["result"] = result
                node_outputs[nid] = out
                node.computed = True
                results[nid] = {"status": "ok", "outputs": out}

            except Exception as e:
                results[nid] = {"status": "error", "error": str(e)[:256]}

        return {"graph": graph.name, "nodes_executed": len(order), "results": results}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniDynamoEngine:
    """
    OMNI Dynamo Engine — Zero-Mock Visual Programming & Computational Design.

    Capabilities (all native stdlib):
      - Node-based graph definition
      - DAG topological sort & execution
      - 30+ built-in operations (math, string, list, logic, geometry)
      - Custom code block nodes
      - Parametric computation
    """

    def __init__(self):
        self.executor = DAGExecutor()
        self.ops = BuiltinOps()

    def create_graph(self, name: str) -> NodeGraph:
        gid = hashlib.sha256(f"{name}{time.time()}".encode()).hexdigest()[:12]
        return NodeGraph(graph_id=gid, name=name, created_at=time.time())

    def execute_graph(self, graph: NodeGraph) -> Dict:
        return self.executor.execute(graph)

    def list_operations(self) -> List[str]:
        return [
            "add", "subtract", "multiply", "divide", "power", "sqrt", "abs",
            "sin", "cos", "round", "min", "max", "clamp",
            "concat", "upper", "lower", "length", "replace",
            "range", "list_sum", "list_avg", "list_sort", "list_reverse", "list_filter",
            "if", "equal", "greater", "not",
            "point", "distance", "midpoint",
            "watch", "to_string",
        ]

    def diagnostics(self) -> Dict:
        return {
            "engine": "OmniDynamoEngine",
            "status": "active",
            "operations": len(self.list_operations()),
            "categories": [c.value for c in NodeCategory],
            "capabilities": ["node_graph", "dag_execute", "topological_sort",
                             "builtin_ops", "custom_code", "parametric"],
        }


if __name__ == "__main__":
    engine = OmniDynamoEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
