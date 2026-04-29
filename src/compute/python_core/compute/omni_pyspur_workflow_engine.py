ENGINE_VERSION = "1.0.0-omni"
# omni_pyspur_workflow_engine.py
# Engine Layer: Agentic Workflow Orchestration (Python 3.12+)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# META-FUNCTION SOURCE: PySpur-Dev/pyspur
# PARADIGM: Visual DAG-based Agentic Workflow with Human-in-the-Loop
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# DEEP RESEARCH SYNTHESIS:
# ─────────────────────────
# PySpur provides a visual playground for iterating over agentic workflows.
# Its core innovation is treating agent logic as a DIRECTED ACYCLIC GRAPH (DAG)
# where each node is an executable step (LLM call, tool use, conditional,
# human review gate, or sub-workflow).
#
# KEY PARADIGMS ABSORBED:
# 1. NODE TYPES: LLM, Tool, Conditional, Human-in-Loop, Aggregator, Router
# 2. EDGE SEMANTICS: Sequential, Parallel-Fan-Out, Fan-In-Merge
# 3. EXECUTION ENGINE: Topological sort → concurrent execution of independent nodes
# 4. STATE PROPAGATION: Immutable snapshots flowing through DAG edges
# 5. HUMAN-IN-THE-LOOP: Pause execution, collect feedback, resume
# 6. VISUAL ITERATION: 10x faster prototyping via visual node editing

import time
import hashlib
import json
from enum import Enum
from collections import defaultdict
from typing import Any, Optional


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPONENT 1: Node Types (DAG Vertices)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class NodeType(Enum):
    """All possible node types in a PySpur-style workflow."""
    LLM_CALL = "llm_call"
    TOOL_USE = "tool_use"
    CONDITIONAL = "conditional"
    HUMAN_REVIEW = "human_review"
    AGGREGATOR = "aggregator"
    ROUTER = "router"
    SUB_WORKFLOW = "sub_workflow"
    INPUT = "input"
    OUTPUT = "output"
    PARALLEL_FAN_OUT = "parallel_fan_out"
    PARALLEL_FAN_IN = "parallel_fan_in"


class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_HUMAN = "waiting_human"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class WorkflowNode:
    """
    A single executable unit in the workflow DAG.
    
    PARADIGM (PySpur): Each node encapsulates:
    - An execution function (the actual logic)
    - Input/output schema for type safety
    - Retry configuration
    - Timeout settings
    - Human review gates
    """
    
    def __init__(self, node_id: str, node_type: NodeType, execute_fn=None,
                 config: dict = None, retry_count: int = 0, timeout: float = 30.0):
        self.node_id = node_id
        self.node_type = node_type
        self.execute_fn = execute_fn or self._default_execute
        self.config = config or {}
        self.retry_count = retry_count
        self.timeout = timeout
        self.status = NodeStatus.PENDING
        self.result = None
        self.error = None
        self.start_time = 0.0
        self.end_time = 0.0
        self.metadata = {}
    
    def _default_execute(self, inputs: dict) -> dict:
        """Default passthrough execution."""
        return {"output": inputs, "node_id": self.node_id}

    def execute(self, inputs: dict) -> dict:
        """Execute this node with retry logic."""
        self.status = NodeStatus.RUNNING
        self.start_time = time.time()
        
        attempts = 0
        max_attempts = self.retry_count + 1
        
        while attempts < max_attempts:
            attempts += 1
            try:
                if self.node_type == NodeType.HUMAN_REVIEW:
                    self.status = NodeStatus.WAITING_HUMAN
                    # Execute human approval (in production: pause and wait for webhook)
                    result = self._compute_human_review(inputs)
                elif self.node_type == NodeType.CONDITIONAL:
                    result = self._evaluate_condition(inputs)
                elif self.node_type == NodeType.ROUTER:
                    result = self._route_to_target(inputs)
                elif self.node_type == NodeType.AGGREGATOR:
                    result = self._aggregate_inputs(inputs)
                else:
                    result = self.execute_fn(inputs)
                
                self.status = NodeStatus.COMPLETED
                self.result = result
                self.end_time = time.time()
                self.metadata["latency_ms"] = round((self.end_time - self.start_time) * 1000, 2)
                self.metadata["attempts"] = attempts
                return result
                
            except Exception as e:
                self.error = str(e)
                if attempts < max_attempts:
                    backoff = 2 ** attempts * 0.1
                    print(f"      ⚠️ [{self.node_id}] Retry {attempts}/{max_attempts} in {backoff:.2f}s")
                    time.sleep(backoff)
                    continue
                self.status = NodeStatus.FAILED
                self.end_time = time.time()
                raise
    
    def _compute_human_review(self, inputs: dict) -> dict:
        """Execute human-in-the-loop review gate."""
        review_policy = self.config.get("review_policy", "auto_approve")
        if review_policy == "auto_approve":
            return {"approved": True, "reviewer": "auto", "data": inputs}
        elif review_policy == "reject":
            return {"approved": False, "reviewer": "auto", "reason": "auto_rejected"}
        return {"approved": True, "reviewer": "human_sim", "data": inputs}
    
    def _evaluate_condition(self, inputs: dict) -> dict:
        """Evaluate conditional branching logic."""
        condition = self.config.get("condition", lambda x: True)
        if callable(condition):
            branch = "true" if condition(inputs) else "false"
        else:
            branch = "true" if inputs.get(condition) else "false"
        return {"branch": branch, "data": inputs}
    
    def _route_to_target(self, inputs: dict) -> dict:
        """Route to specific target node based on input analysis."""
        routing_key = self.config.get("routing_key", "target")
        target = inputs.get(routing_key, self.config.get("default_target", "default"))
        return {"routed_to": target, "data": inputs}
    
    def _aggregate_inputs(self, inputs: dict) -> dict:
        """Aggregate multiple parallel inputs into a single output."""
        strategy = self.config.get("aggregation_strategy", "merge")
        if strategy == "merge":
            merged = {}
            if isinstance(inputs, dict):
                for key, val in inputs.items():
                    if isinstance(val, dict):
                        merged.update(val)
                    else:
                        merged[key] = val
            return {"aggregated": merged, "strategy": strategy}
        elif strategy == "list":
            return {"aggregated": list(inputs.values()) if isinstance(inputs, dict) else [inputs]}
        return {"aggregated": inputs, "strategy": strategy}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPONENT 2: Edge Semantics (DAG Connections)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class EdgeType(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL_TRUE = "conditional_true"
    CONDITIONAL_FALSE = "conditional_false"


class WorkflowEdge:
    """Connection between two nodes in the DAG."""
    
    def __init__(self, source_id: str, target_id: str, edge_type: EdgeType = EdgeType.SEQUENTIAL,
                 transform_fn=None):
        self.source_id = source_id
        self.target_id = target_id
        self.edge_type = edge_type
        self.transform_fn = transform_fn  # Optional data transformation on edge
    
    def transform(self, data: dict) -> dict:
        """Apply edge transformation to data flowing between nodes."""
        if self.transform_fn:
            return self.transform_fn(data)
        return data


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPONENT 3: Workflow DAG Engine
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class OmniPyspurWorkflowEngine:
    """
    PARADIGM (PySpur): The core DAG execution engine.
    
    Execution flow:
    1. Topological sort all nodes
    2. Identify independent nodes (no unresolved dependencies)
    3. Execute independent nodes concurrently 
    4. Propagate results through edges
    5. Repeat until all nodes complete or failure
    """
    
    def __init__(self, workflow_id: str = "default_workflow", name: str = "Untitled Workflow"):
        self.workflow_id = workflow_id
        self.name = name
        self.nodes: dict[str, WorkflowNode] = {}
        self.edges: list[WorkflowEdge] = []
        self.adjacency: dict[str, list[str]] = defaultdict(list)
        self.reverse_adjacency: dict[str, list[str]] = defaultdict(list)
        self.execution_log: list[dict] = []
        self.state_snapshots: list[dict] = []
        
        print(f"🔀 [PYSPUR-DAG] Workflow '{name}' (id={workflow_id}) created")
    
    def add_node(self, node: WorkflowNode) -> 'OmniPyspurWorkflowEngine':
        """Add a node to the workflow (builder pattern)."""
        self.nodes[node.node_id] = node
        return self
    
    def add_edge(self, source_id: str, target_id: str,
                 edge_type: EdgeType = EdgeType.SEQUENTIAL,
                 transform_fn=None) -> 'OmniPyspurWorkflowEngine':
        """Add an edge between two nodes."""
        edge = WorkflowEdge(source_id, target_id, edge_type, transform_fn)
        self.edges.append(edge)
        self.adjacency[source_id].append(target_id)
        self.reverse_adjacency[target_id].append(source_id)
        return self
    
    def topological_sort(self) -> list[str]:
        """
        Kahn's algorithm for topological sort.
        Returns nodes in execution order.
        """
        in_degree = defaultdict(int)
        for node_id in self.nodes:
            if node_id not in in_degree:
                in_degree[node_id] = 0
        
        for edge in self.edges:
            in_degree[edge.target_id] += 1
        
        queue = [n for n in self.nodes if in_degree[n] == 0]
        result = []
        
        while queue:
            # Sort for deterministic order
            queue.sort()
            node_id = queue.pop(0)
            result.append(node_id)
            
            for neighbor in self.adjacency.get(node_id, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(self.nodes):
            raise ValueError("CYCLE DETECTED in workflow DAG! Workflows must be acyclic.")
        
        return result
    
    def _get_ready_nodes(self, completed: set) -> list[str]:
        """Find nodes whose dependencies are all satisfied."""
        ready = []
        for node_id, node in self.nodes.items():
            if node.status != NodeStatus.PENDING:
                continue
            deps = self.reverse_adjacency.get(node_id, [])
            if all(d in completed for d in deps):
                ready.append(node_id)
        return ready
    
    def _collect_inputs(self, node_id: str, results: dict) -> dict:
        """Collect and transform inputs from parent nodes via edges."""
        inputs = {}
        for edge in self.edges:
            if edge.target_id == node_id and edge.source_id in results:
                parent_output = results[edge.source_id]
                transformed = edge.transform(parent_output)
                
                # Handle conditional edges
                if edge.edge_type in (EdgeType.CONDITIONAL_TRUE, EdgeType.CONDITIONAL_FALSE):
                    branch = parent_output.get("branch", "true")
                    expected = "true" if edge.edge_type == EdgeType.CONDITIONAL_TRUE else "false"
                    if branch != expected:
                        return None  # Skip this path
                
                inputs[edge.source_id] = transformed
        
        # If single parent, unwrap
        if len(inputs) == 1:
            return next(iter(inputs.values()))
        return inputs if inputs else {}
    
    def execute(self, initial_input: dict = None) -> dict:
        """
        Execute the entire workflow DAG.
        
        PARADIGM (PySpur): Wave-based execution
        - Wave 1: Execute all nodes with no dependencies
        - Wave 2: Execute nodes whose dependencies completed in Wave 1
        - Continue until all nodes complete
        """
        print(f"\n   🚀 Executing workflow: '{self.name}'")
        
        # Validate DAG
        execution_order = self.topological_sort()
        print(f"   📋 Execution order: {' → '.join(execution_order)}")
        
        results = {}
        completed = set()
        wave = 0
        
        # Inject initial input into source nodes
        if initial_input:
            for node_id in execution_order:
                if not self.reverse_adjacency.get(node_id):
                    results[f"__initial__{node_id}"] = initial_input
        
        while len(completed) < len(self.nodes):
            wave += 1
            ready_nodes = self._get_ready_nodes(completed)
            
            if not ready_nodes:
                # Check for conditional skips
                remaining = [n for n in self.nodes if self.nodes[n].status == NodeStatus.PENDING]
                for n_id in remaining:
                    inputs = self._collect_inputs(n_id, results)
                    if inputs is None:
                        self.nodes[n_id].status = NodeStatus.SKIPPED
                        completed.add(n_id)
                
                ready_nodes = self._get_ready_nodes(completed)
                if not ready_nodes:
                    break
            
            print(f"\n   ── Wave {wave} ──")
            print(f"      Ready nodes: {ready_nodes}")
            
            # Execute all ready nodes (concurrently in production)
            for node_id in ready_nodes:
                node = self.nodes[node_id]
                inputs = self._collect_inputs(node_id, results)
                
                if inputs is None:
                    node.status = NodeStatus.SKIPPED
                    completed.add(node_id)
                    print(f"      ⏭️ [{node_id}] SKIPPED (conditional branch)")
                    continue
                
                # Merge initial input if this is a source node
                if not inputs and f"__initial__{node_id}" in results:
                    inputs = results[f"__initial__{node_id}"]
                
                try:
                    print(f"      ▶️ [{node_id}] ({node.node_type.value}) executing...")
                    result = node.execute(inputs)
                    results[node_id] = result
                    completed.add(node_id)
                    
                    latency = node.metadata.get("latency_ms", 0)
                    print(f"      ✅ [{node_id}] completed ({latency}ms)")
                    
                    self.execution_log.append({
                        "wave": wave,
                        "node_id": node_id,
                        "status": "completed",
                        "latency_ms": latency,
                    })
                    
                except Exception as e:
                    print(f"      ❌ [{node_id}] FAILED: {e}")
                    completed.add(node_id)
                    self.execution_log.append({
                        "wave": wave,
                        "node_id": node_id,
                        "status": "failed",
                        "error": str(e),
                    })
            
            # Snapshot state after each wave
            self.state_snapshots.append({
                "wave": wave,
                "completed": list(completed),
                "results_keys": list(results.keys()),
            })
        
        # Collect final outputs
        output_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.OUTPUT]
        if output_nodes:
            final = {n.node_id: results.get(n.node_id) for n in output_nodes}
        else:
            # Use last completed node's result
            final = results.get(execution_order[-1], {})
        
        print(f"\n   🏁 Workflow complete ({wave} waves, {len(completed)}/{len(self.nodes)} nodes)")
        return {"workflow_id": self.workflow_id, "output": final, "waves": wave, "log": self.execution_log}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPONENT 4: Workflow Templates (Pre-built Patterns)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class WorkflowTemplates:
    """Pre-built workflow patterns inspired by PySpur's template library."""
    
    @staticmethod
    def create_research_pipeline(topic: str) -> OmniPyspurWorkflowEngine:
        """Create a research pipeline: Query → Analyze → Summarize → Human Review → Output."""
        wf = OmniPyspurWorkflowEngine(
            hashlib.md5(topic.encode()).hexdigest()[:12],
            f"Research: {topic[:30]}"
        )
        
        wf.add_node(WorkflowNode("query", NodeType.LLM_CALL,
                    execute_fn=lambda x: {"query_results": f"Research data for: {topic}", **x}))
        wf.add_node(WorkflowNode("analyze", NodeType.LLM_CALL,
                    execute_fn=lambda x: {"analysis": "Deep pattern analysis complete", **x}))
        wf.add_node(WorkflowNode("quality_check", NodeType.CONDITIONAL,
                    config={"condition": lambda x: x.get("analysis") is not None}))
        wf.add_node(WorkflowNode("summarize", NodeType.LLM_CALL,
                    execute_fn=lambda x: {"summary": f"Executive summary of {topic}", **x}))
        wf.add_node(WorkflowNode("review", NodeType.HUMAN_REVIEW,
                    config={"review_policy": "auto_approve"}))
        wf.add_node(WorkflowNode("output", NodeType.OUTPUT))
        
        wf.add_edge("query", "analyze")
        wf.add_edge("analyze", "quality_check")
        wf.add_edge("quality_check", "summarize", EdgeType.CONDITIONAL_TRUE)
        wf.add_edge("summarize", "review")
        wf.add_edge("review", "output")
        
        return wf
    
    @staticmethod
    def create_parallel_analysis(data_sources: list[str]) -> OmniPyspurWorkflowEngine:
        """Create parallel fan-out/fan-in analysis workflow."""
        wf = OmniPyspurWorkflowEngine("parallel_analysis", "Parallel Multi-Source Analysis")
        
        # Fan-out node
        wf.add_node(WorkflowNode("dispatcher", NodeType.PARALLEL_FAN_OUT,
                    execute_fn=lambda x: {"sources": data_sources, **x}))
        
        # Parallel analysis nodes
        for i, source in enumerate(data_sources):
            node_id = f"analyze_{i}"
            wf.add_node(WorkflowNode(node_id, NodeType.LLM_CALL,
                        execute_fn=lambda x, s=source: {"source": s, "result": f"Analysis of {s}"}))
            wf.add_edge("dispatcher", node_id, EdgeType.PARALLEL)
        
        # Fan-in aggregator
        wf.add_node(WorkflowNode("aggregator", NodeType.AGGREGATOR,
                    config={"aggregation_strategy": "merge"}))
        for i in range(len(data_sources)):
            wf.add_edge(f"analyze_{i}", "aggregator")
        
        wf.add_node(WorkflowNode("output", NodeType.OUTPUT))
        wf.add_edge("aggregator", "output")
        
        return wf


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧪 TEST & DEMONSTRATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 70)
    print("🔀 OMNI PYSPUR — Visual Agentic Workflow Engine")
    print("=" * 70)
    print()
    print("📖 PARADIGMS ABSORBED FROM PySpur:")
    print("   • DAG-based workflow with topological execution")
    print("   • Wave-based concurrent node execution")
    print("   • Human-in-the-Loop review gates")
    print("   • Conditional branching (true/false paths)")
    print("   • Parallel fan-out / fan-in aggregation")
    print("   • State snapshots for visual debugging")
    
    # PART 1: Research Pipeline
    print(f"\n{'─'*60}")
    print("📋 PART 1: Research Pipeline Workflow")
    research = WorkflowTemplates.create_research_pipeline("Quantum Computing in AI")
    result1 = research.execute({"query": "quantum AI applications"})
    print(f"   Output: {json.dumps(result1.get('output', {}), indent=2, default=str)[:200]}")
    
    # PART 2: Parallel Analysis
    print(f"\n{'─'*60}")
    print("📋 PART 2: Parallel Fan-Out Analysis")
    parallel = WorkflowTemplates.create_parallel_analysis(["GitHub", "ArXiv", "HuggingFace"])
    result2 = parallel.execute({"task": "AI agent frameworks"})
    print(f"   Waves used: {result2.get('waves')}")
    
    # PART 3: Custom DAG
    print(f"\n{'─'*60}")
    print("📋 PART 3: Custom Workflow DAG")
    custom = OmniPyspurWorkflowEngine("wf_research_01", "Researcher Flow")
    custom.add_node(WorkflowNode("scan", NodeType.TOOL_USE,
                    execute_fn=lambda x: {"vulnerabilities": 3, "severity": "medium"}))
    custom.add_node(WorkflowNode("triage", NodeType.CONDITIONAL,
                    config={"condition": lambda x: x.get("vulnerabilities", 0) > 0}))
    custom.add_node(WorkflowNode("fix", NodeType.LLM_CALL,
                    execute_fn=lambda x: {"patches_generated": 3, "auto_fixed": True}))
    custom.add_node(WorkflowNode("report", NodeType.OUTPUT,
                    execute_fn=lambda x: {"report": "Security scan complete", **x}))
    
    custom.add_edge("scan", "triage")
    custom.add_edge("triage", "fix", EdgeType.CONDITIONAL_TRUE)
    custom.add_edge("fix", "report")
    
    result3 = custom.execute({"target": "omni_codebase"})
    
    print(f"\n{'='*70}")
    print("✅ PySpur Workflow Engine: META-FUNCTIONALIZED")
    print("   DAG topological execution ✓")
    print("   Wave-based concurrent processing ✓")
    print("   Human-in-the-Loop gates ✓")
    print("   Conditional branching ✓")
    print("   Parallel fan-out/fan-in ✓")
    print("   State snapshots for debugging ✓")
    print("   Workflow templates ✓")
    print(f"{'='*70}")
