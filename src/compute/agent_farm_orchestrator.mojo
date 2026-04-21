// ===========================================================================
// OMNI COMPUTE LAYER — AGENT FARM ORCHESTRATOR
// ===========================================================================
// Source Paradigm : Multi-agent orchestration patterns
// Domain Layer   : Compute (AI-first high-performance programming)
// Language        : Mojo
// Function        : AI agent farm orchestrator that manages pools of
//                   autonomous agents, distributes tasks, tracks health,
//                   aggregates results, and handles agent lifecycle
// ===========================================================================

from collections import List, Dict, Optional
from time import now

// ---- Agent Types ----------------------------------------------------------

@value
struct AgentCapability:
    var name: String
    var version: String
    var max_concurrent: Int

    fn __init__(inout self, name: String, version: String, max_concurrent: Int = 1):
        self.name = name
        self.version = version
        self.max_concurrent = max_concurrent

@value
struct AgentConfig:
    var agent_id: String
    var agent_type: String         // "worker", "supervisor", "router"
    var model: String              // LLM model name
    var temperature: Float64
    var max_tokens: Int
    var capabilities: List[AgentCapability]
    var system_prompt: String

    fn __init__(inout self, agent_id: String, agent_type: String,
                model: String, temperature: Float64 = 0.7,
                max_tokens: Int = 4096, system_prompt: String = ""):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.capabilities = List[AgentCapability]()
        self.system_prompt = system_prompt

// ---- Task Models ----------------------------------------------------------

@value
struct AgentTask:
    var task_id: String
    var description: String
    var priority: Int              // 1 (highest) to 10 (lowest)
    var required_capability: String
    var input_data: String
    var max_retries: Int
    var timeout_seconds: Int

    fn __init__(inout self, task_id: String, description: String,
                priority: Int = 5, capability: String = "general",
                input_data: String = "", max_retries: Int = 3,
                timeout_seconds: Int = 300):
        self.task_id = task_id
        self.description = description
        self.priority = priority
        self.required_capability = capability
        self.input_data = input_data
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

@value
struct TaskResult:
    var task_id: String
    var agent_id: String
    var success: Bool
    var output: String
    var error: String
    var elapsed_ms: Float64
    var retries_used: Int

// ---- Agent Health ---------------------------------------------------------

@value
struct AgentHealth:
    var agent_id: String
    var status: String             // "idle", "busy", "error", "offline"
    var tasks_completed: Int
    var tasks_failed: Int
    var avg_response_ms: Float64
    var uptime_seconds: Float64
    var last_heartbeat_ms: Float64

    fn success_rate(self) -> Float64:
        let total = self.tasks_completed + self.tasks_failed
        if total == 0:
            return 1.0
        return Float64(self.tasks_completed) / Float64(total)

// ---- Farm Orchestrator ----------------------------------------------------

struct AgentFarmOrchestrator:
    var agents: Dict[String, AgentConfig]
    var health: Dict[String, AgentHealth]
    var task_queue: List[AgentTask]
    var results: List[TaskResult]
    var total_dispatched: Int

    fn __init__(inout self):
        self.agents = Dict[String, AgentConfig]()
        self.health = Dict[String, AgentHealth]()
        self.task_queue = List[AgentTask]()
        self.results = List[TaskResult]()
        self.total_dispatched = 0
        print("[FARM-OMNI-MOJO] Agent farm orchestrator initialized.")

    fn register_agent(inout self, config: AgentConfig):
        """Register a new agent into the farm."""
        self.agents[config.agent_id] = config
        self.health[config.agent_id] = AgentHealth(
            agent_id=config.agent_id,
            status="idle",
            tasks_completed=0,
            tasks_failed=0,
            avg_response_ms=0.0,
            uptime_seconds=0.0,
            last_heartbeat_ms=0.0,
        )
        print("[FARM-OMNI-MOJO] Registered agent: " + config.agent_id
              + " (" + config.agent_type + ", model: " + config.model + ")")

    fn submit_task(inout self, task: AgentTask):
        """Add a task to the queue."""
        self.task_queue.append(task)
        print("[FARM-OMNI-MOJO] Task queued: " + task.task_id
              + " (priority: " + String(task.priority) + ")")

    fn find_available_agent(self, capability: String) -> Optional[String]:
        """Find an idle agent with the required capability."""
        for entry in self.health.items():
            let agent_id = entry[].key
            let h = entry[].value
            if h.status == "idle":
                if agent_id in self.agents:
                    let config = self.agents[agent_id]
                    for cap in config.capabilities:
                        if cap.name == capability:
                            return agent_id
        return None

    fn dispatch_next(inout self) -> Optional[TaskResult]:
        """Dispatch the highest-priority task to an available agent."""
        if len(self.task_queue) == 0:
            return None

        // Find highest priority task
        var best_idx: Int = 0
        var best_priority: Int = 999
        for i in range(len(self.task_queue)):
            if self.task_queue[i].priority < best_priority:
                best_priority = self.task_queue[i].priority
                best_idx = i

        let task = self.task_queue[best_idx]
        let agent_opt = self.find_available_agent(task.required_capability)

        if not agent_opt:
            print("[FARM-OMNI-MOJO] No available agent for capability: "
                  + task.required_capability)
            return None

        let agent_id = agent_opt.value()
        self.task_queue.pop(best_idx)
        self.total_dispatched += 1

        // Mark agent busy
        self.health[agent_id].status = "busy"

        print("[FARM-OMNI-MOJO] Dispatched: " + task.task_id + " → " + agent_id)

        // Production: send task to agent via gRPC/HTTP, await response
        let result = TaskResult(
            task_id=task.task_id,
            agent_id=agent_id,
            success=True,
            output="Task completed successfully",
            error="",
            elapsed_ms=42.0,
            retries_used=0,
        )

        // Update health
        self.health[agent_id].status = "idle"
        self.health[agent_id].tasks_completed += 1
        self.results.append(result)

        return result

    fn process_all(inout self) -> Int:
        """Process all queued tasks."""
        print("[FARM-OMNI-MOJO] Processing " + String(len(self.task_queue)) + " task(s)...")
        var processed: Int = 0
        while len(self.task_queue) > 0:
            let result = self.dispatch_next()
            if not result:
                break
            processed += 1
        print("[FARM-OMNI-MOJO] Processed " + String(processed) + " task(s).")
        return processed

    fn get_farm_stats(self) -> Dict[String, Int]:
        """Return aggregated farm statistics."""
        var stats = Dict[String, Int]()
        stats["total_agents"] = len(self.agents)
        stats["total_dispatched"] = self.total_dispatched
        stats["queue_depth"] = len(self.task_queue)
        stats["total_results"] = len(self.results)
        return stats
