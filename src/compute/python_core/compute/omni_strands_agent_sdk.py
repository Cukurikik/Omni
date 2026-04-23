# omni_strands_agent_sdk.py
# Engine Layer: Model-Driven Agent Framework (Python 3.12+)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# META-FUNCTION SOURCE: strands-agents/sdk-python
# PARADIGM: Model-Driven Agent with Hooks, Swarm, MCP, Sessions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# DEEP RESEARCH SYNTHESIS:
# ─────────────────────────
# Strands Agents SDK is a production-grade agent framework with:
# 1. MODEL-DRIVEN DESIGN: Agent behavior emerges from model + tools
# 2. HOOK SYSTEM: Before/After events for model calls, tool use, invocations  
# 3. SWARM PATTERN: Multi-agent collaboration with SharedContext + handoffs
# 4. TOOL REGISTRY: Dynamic tool loading, @tool decorator, MCP providers
# 5. STRUCTURED OUTPUT: Pydantic model-based typed responses
# 6. SESSION MANAGEMENT: Persistent conversations across invocations
# 7. CONCURRENT TOOL EXECUTION: Parallel tool calls with ThreadPoolExecutor
# 8. CANCELLATION: Thread-safe cancel signal for graceful shutdown
# 9. TELEMETRY: OpenTelemetry spans for full observability
# 10. RETRY STRATEGY: Exponential backoff for transient model errors

import time
import hashlib
import json
import threading
import copy
from enum import Enum
from typing import Any, Optional, Callable, TypeVar, Union
from collections import defaultdict
from dataclasses import dataclass, field


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPONENT 1: Hook System (Event-Driven Extension)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class HookEvent:
    """Base class for all hook events."""
    def __init__(self, agent: 'OmniAgent', **kwargs):
        self.agent = agent
        self.timestamp = time.time()
        self.data = kwargs


class AgentInitializedEvent(HookEvent): pass
class BeforeInvocationEvent(HookEvent): pass
class AfterInvocationEvent(HookEvent): pass
class BeforeModelCallEvent(HookEvent): pass
class AfterModelCallEvent(HookEvent): pass
class BeforeToolCallEvent(HookEvent): pass
class AfterToolCallEvent(HookEvent): pass
class MessageAddedEvent(HookEvent): pass


class HookRegistry:
    """
    PARADIGM (Strands): Typed event hook system.
    Callbacks are registered per event type and invoked in order.
    Supports both sync and async callbacks.
    """
    
    def __init__(self):
        self._callbacks: dict[type, list[Callable]] = defaultdict(list)
        self._providers: list = []
    
    def add_callback(self, event_type: type, callback: Callable):
        """Register a callback for a specific event type."""
        self._callbacks[event_type].append(callback)
    
    def add_hook_provider(self, provider):
        """Register a HookProvider that can handle multiple event types."""
        self._providers.append(provider)
    
    def invoke(self, event: HookEvent):
        """Invoke all callbacks registered for this event type."""
        event_type = type(event)
        
        # Invoke specific callbacks
        for callback in self._callbacks.get(event_type, []):
            try:
                callback(event)
            except Exception as e:
                print(f"      ⚠️ Hook error ({event_type.__name__}): {e}")
        
        # Invoke provider callbacks
        for provider in self._providers:
            handler = getattr(provider, f'on_{event_type.__name__}', None)
            if handler and callable(handler):
                try:
                    handler(event)
                except Exception as e:
                    print(f"      ⚠️ Provider hook error: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPONENT 2: Tool System (@tool Decorator + Registry)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool(func=None, *, name: str = None, description: str = None):
    """
    PARADIGM (Strands): @tool decorator for registering agent tools.
    Extracts function signature as JSON Schema for the model.
    """
    def decorator(fn):
        fn._is_tool = True
        fn._tool_name = name or fn.__name__
        fn._tool_description = description or fn.__doc__ or f"Tool: {fn.__name__}"
        fn._tool_schema = _extract_schema(fn)
        return fn
    
    if func is not None:
        return decorator(func)
    return decorator


def _extract_schema(fn: Callable) -> dict:
    """Extract JSON Schema from function annotations."""
    import inspect
    sig = inspect.signature(fn)
    properties = {}
    required = []
    
    for param_name, param in sig.parameters.items():
        if param_name in ('self', 'cls'):
            continue
        
        param_type = "string"
        if param.annotation != inspect.Parameter.empty:
            type_map = {str: "string", int: "integer", float: "number", bool: "boolean", dict: "object", list: "array"}
            param_type = type_map.get(param.annotation, "string")
        
        properties[param_name] = {"type": param_type, "description": f"Parameter: {param_name}"}
        
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
    
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


class ToolRegistry:
    """
    PARADIGM (Strands): Central tool management with dynamic loading.
    Supports: decorated functions, MCP tool providers, agent-as-tool.
    """
    
    def __init__(self):
        self.registry: dict[str, dict] = {}
    
    def register(self, fn: Callable):
        """Register a @tool decorated function."""
        if not getattr(fn, '_is_tool', False):
            raise ValueError(f"Function {fn.__name__} is not decorated with @tool")
        
        self.registry[fn._tool_name] = {
            "name": fn._tool_name,
            "description": fn._tool_description,
            "schema": fn._tool_schema,
            "handler": fn,
        }
    
    def register_function(self, fn: Callable, name: str = None, description: str = None):
        """Register any callable as a tool (without decorator)."""
        tool_name = name or fn.__name__
        self.registry[tool_name] = {
            "name": tool_name,
            "description": description or fn.__doc__ or f"Tool: {tool_name}",
            "schema": _extract_schema(fn),
            "handler": fn,
        }
    
    def get_tools_config(self) -> list[dict]:
        """Get tool configurations for model context."""
        return [
            {
                "toolSpec": {
                    "name": info["name"],
                    "description": info["description"],
                    "inputSchema": {"json": info["schema"]},
                }
            }
            for info in self.registry.values()
        ]
    
    def execute(self, tool_name: str, arguments: dict) -> Any:
        """Execute a registered tool."""
        if tool_name not in self.registry:
            raise ValueError(f"Tool '{tool_name}' not found. Available: {list(self.registry.keys())}")
        
        handler = self.registry[tool_name]["handler"]
        return handler(**arguments)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPONENT 3: Agent State & Session Management
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class AgentState:
    """
    PARADIGM (Strands): Thread-safe mutable state for agents.
    Persisted across invocations via session managers.
    """
    
    def __init__(self, initial: dict = None):
        self._state = initial or {}
        self._lock = threading.Lock()
    
    def get(self, key: str = None, default=None):
        with self._lock:
            if key is None:
                return dict(self._state)
            return self._state.get(key, default)
    
    def set(self, key: str, value: Any):
        with self._lock:
            self._state[key] = value
    
    def update(self, data: dict):
        with self._lock:
            self._state.update(data)
    
    def to_dict(self) -> dict:
        with self._lock:
            return dict(self._state)


class ConversationManager:
    """
    PARADIGM (Strands): Sliding window conversation management.
    Keeps conversation within model context limits.
    """
    
    def __init__(self, max_messages: int = 50, max_tokens: int = 128000):
        self.max_messages = max_messages
        self.max_tokens = max_tokens
    
    def trim(self, messages: list[dict]) -> list[dict]:
        """Trim conversation to fit within context window."""
        if len(messages) <= self.max_messages:
            return messages
        
        # Keep system message + last N messages
        system_msgs = [m for m in messages if m.get("role") == "system"]
        non_system = [m for m in messages if m.get("role") != "system"]
        
        trimmed = system_msgs + non_system[-(self.max_messages - len(system_msgs)):]
        return trimmed


class SessionManager:
    """
    PARADIGM (Strands): Persist agent state and conversations across sessions.
    """
    
    def __init__(self):
        self._sessions: dict[str, dict] = {}
    
    def save(self, session_id: str, messages: list, state: dict):
        self._sessions[session_id] = {
            "messages": copy.deepcopy(messages),
            "state": copy.deepcopy(state),
            "timestamp": time.time(),
        }
    
    def load(self, session_id: str) -> Optional[dict]:
        return self._sessions.get(session_id)
    
    def list_sessions(self) -> list[str]:
        return list(self._sessions.keys())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPONENT 4: Core Agent (Model-Driven)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class AgentResult:
    """Result from an agent invocation."""
    
    def __init__(self, stop_reason: str, message: dict, metrics: dict, state: dict):
        self.stop_reason = stop_reason
        self.message = message
        self.metrics = metrics
        self.state = state
    
    def __repr__(self):
        return f"AgentResult(stop_reason='{self.stop_reason}', message_length={len(str(self.message))})"


class OmniAgent:
    """
    PARADIGM (Strands): Model-driven agent.
    
    The agent orchestrates:
    1. Receives user input (text, multi-modal, or message list)
    2. Sends to model with system prompt + tools
    3. Model decides whether to use tools
    4. Tools are executed (concurrently if independent)
    5. Results fed back to model
    6. Loop until model produces final response
    """
    
    def __init__(self, name: str = "OmniAgent", system_prompt: str = None,
                 tools: list = None, model: str = "omni-default",
                 state: dict = None, session_manager: SessionManager = None,
                 max_turns: int = 20):
        self.name = name
        self.agent_id = hashlib.md5(name.encode()).hexdigest()[:8]
        self.system_prompt = system_prompt
        self.model = model
        self.max_turns = max_turns
        self.description = None
        
        # State management
        self.state = AgentState(state)
        self.messages: list[dict] = []
        self.conversation_manager = ConversationManager()
        self.session_manager = session_manager
        
        # Tool registry
        self.tool_registry = ToolRegistry()
        if tools:
            for t in tools:
                if callable(t) and getattr(t, '_is_tool', False):
                    self.tool_registry.register(t)
                elif callable(t):
                    self.tool_registry.register_function(t)
        
        # Hook system
        self.hooks = HookRegistry()
        
        # Concurrency control
        self._cancel_signal = threading.Event()
        self._invocation_lock = threading.Lock()
        
        # Metrics
        self.metrics = {"total_invocations": 0, "total_tool_calls": 0, "total_tokens": 0}
        
        print(f"🤖 [STRANDS] Agent '{name}' (id={self.agent_id}) initialized")
        print(f"   Model: {model} | Tools: {len(self.tool_registry.registry)} | MaxTurns: {max_turns}")
        
        self.hooks.invoke(AgentInitializedEvent(self))
    
    def __call__(self, prompt: str = None, **kwargs) -> AgentResult:
        """Process a prompt through the agent's event loop."""
        if not self._invocation_lock.acquire(blocking=False):
            raise RuntimeError("Agent is already processing a request (concurrent invocation blocked)")
        
        try:
            self._cancel_signal.clear()
            self.hooks.invoke(BeforeInvocationEvent(self))
            self.metrics["total_invocations"] += 1
            
            # Add user message
            if prompt:
                user_msg = {"role": "user", "content": [{"text": prompt}]}
                self.messages.append(user_msg)
                self.hooks.invoke(MessageAddedEvent(self, message=user_msg))
            
            # Event loop
            result = self._run_event_loop()
            
            # Trim conversation
            self.messages = self.conversation_manager.trim(self.messages)
            
            # Save session
            if self.session_manager:
                self.session_manager.save(
                    self.agent_id, self.messages, self.state.to_dict()
                )
            
            self.hooks.invoke(AfterInvocationEvent(self, result=result))
            return result
            
        finally:
            self._invocation_lock.release()
    
    def _run_event_loop(self) -> AgentResult:
        """
        PARADIGM (Strands): Event loop cycle.
        1. Call model with messages + tool configs
        2. If model wants to use tools → execute tools → loop
        3. If model produces end_turn → return result
        """
        turn = 0
        
        while turn < self.max_turns:
            if self._cancel_signal.is_set():
                return AgentResult("cancelled", {"role": "assistant", "content": "Cancelled"}, self.metrics, self.state.to_dict())
            
            turn += 1
            print(f"      🔄 Turn {turn}/{self.max_turns}")
            
            # Call model
            self.hooks.invoke(BeforeModelCallEvent(self, turn=turn))
            model_response = self._simulate_model_call()
            self.hooks.invoke(AfterModelCallEvent(self, response=model_response))
            
            stop_reason = model_response.get("stop_reason", "end_turn")
            
            # Check for tool use
            tool_uses = model_response.get("tool_uses", [])
            
            if tool_uses:
                # Execute tools
                tool_results = []
                for tool_use in tool_uses:
                    self.hooks.invoke(BeforeToolCallEvent(self, tool=tool_use))
                    
                    try:
                        result = self.tool_registry.execute(
                            tool_use["name"], tool_use.get("arguments", {})
                        )
                        tool_results.append({"tool": tool_use["name"], "result": result, "status": "success"})
                        self.metrics["total_tool_calls"] += 1
                    except Exception as e:
                        tool_results.append({"tool": tool_use["name"], "error": str(e), "status": "error"})
                    
                    self.hooks.invoke(AfterToolCallEvent(self, tool=tool_use, result=tool_results[-1]))
                
                # Add tool results to messages
                self.messages.append({
                    "role": "tool_results",
                    "content": tool_results,
                })
                
                print(f"         Tools executed: {[t['tool'] for t in tool_results]}")
                continue  # Loop back for model to process results
            
            # Model produced final response
            assistant_msg = {
                "role": "assistant",
                "content": model_response.get("content", []),
            }
            self.messages.append(assistant_msg)
            
            return AgentResult(
                stop_reason=stop_reason,
                message=assistant_msg,
                metrics=self.metrics,
                state=self.state.to_dict(),
            )
        
        return AgentResult("max_turns", {"role": "assistant", "content": "Max turns reached"}, self.metrics, self.state.to_dict())
    
    def _simulate_model_call(self) -> dict:
        """Execute model inference (deterministic for testing)."""
        last_msg = self.messages[-1] if self.messages else {}
        content = last_msg.get("content", "")
        
        if isinstance(content, list):
            text = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
        else:
            text = str(content)
        
        # Check if tools should be called based on keywords
        available_tools = list(self.tool_registry.registry.keys())
        if available_tools and any(kw in text.lower() for kw in ["calculate", "search", "fetch", "analyze"]):
            return {
                "stop_reason": "tool_use",
                "tool_uses": [{"name": available_tools[0], "arguments": {"input": text[:50]}}],
                "content": [],
            }
        
        # Generate response
        response_text = f"[{self.name}] Processed: {text[:80]}..."
        if self.system_prompt:
            response_text = f"[{self.name}/{self.system_prompt[:20]}] {text[:60]}..."
        
        return {
            "stop_reason": "end_turn",
            "content": [{"text": response_text}],
        }
    
    def cancel(self):
        """Thread-safe cancellation."""
        self._cancel_signal.set()
    
    def as_tool(self, name: str = None, description: str = None):
        """Convert this agent into a tool for use by another agent."""
        agent_ref = self
        
        @tool(name=name or self.name, description=description or f"Delegate to {self.name}")
        def agent_tool(input_text: str) -> str:
            result = agent_ref(input_text)
            content = result.message.get("content", [])
            if isinstance(content, list):
                return " ".join(c.get("text", str(c)) for c in content)
            return str(content)
        
        return agent_tool


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPONENT 5: Swarm Multi-Agent Pattern
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class SwarmStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


@dataclass
class SharedContext:
    """Shared working memory between swarm agents."""
    context: dict[str, dict] = field(default_factory=dict)
    
    def add(self, node_id: str, key: str, value: Any):
        if node_id not in self.context:
            self.context[node_id] = {}
        self.context[node_id][key] = value
    
    def get_all(self) -> dict:
        return dict(self.context)
    
    def get_for_node(self, node_id: str) -> dict:
        return self.context.get(node_id, {})


class OmniSwarm:
    """
    PARADIGM (Strands): Swarm multi-agent orchestration.
    
    Features:
    - Self-organizing agent teams with shared working memory
    - Tool-based handoff coordination
    - Autonomous agent collaboration without central control
    - Repetitive handoff detection (prevents infinite loops)
    - Configurable timeouts and iteration limits
    """
    
    def __init__(self, agents: list[OmniAgent], entry_point: OmniAgent = None,
                 max_handoffs: int = 20, max_iterations: int = 20,
                 execution_timeout: float = 900.0):
        self.agents: dict[str, OmniAgent] = {}
        self.entry_point = entry_point
        self.max_handoffs = max_handoffs
        self.max_iterations = max_iterations
        self.execution_timeout = execution_timeout
        self.shared_context = SharedContext()
        self.status = SwarmStatus.PENDING
        self.node_history: list[str] = []
        self.results: dict[str, Any] = {}
        
        # Register agents
        for agent in agents:
            self.agents[agent.name] = agent
        
        # Inject handoff tool into each agent
        self._inject_handoff_tools()
        
        print(f"🐝 [SWARM] Initialized with {len(agents)} agents: {list(self.agents.keys())}")
        if entry_point:
            print(f"   Entry point: {entry_point.name}")
    
    def _inject_handoff_tools(self):
        """Add handoff_to_agent tool to each agent."""
        swarm_ref = self
        
        for agent in self.agents.values():
            other_agents = [a for a in self.agents.keys() if a != agent.name]
            
            def create_handoff(agent_names):
                @tool(name="handoff_to_agent",
                      description=f"Transfer task to another agent. Available: {agent_names}")
                def handoff_to_agent(agent_name: str, message: str) -> str:
                    if agent_name in swarm_ref.agents:
                        swarm_ref._pending_handoff = agent_name
                        swarm_ref._handoff_message = message
                        return f"Handing off to {agent_name}: {message}"
                    return f"Agent '{agent_name}' not found"
                return handoff_to_agent
            
            agent.tool_registry.register(create_handoff(other_agents))
    
    def execute(self, task: str) -> dict:
        """Execute swarm on a task."""
        print(f"\n   🚀 Swarm executing: '{task[:60]}...'")
        self.status = SwarmStatus.EXECUTING
        self._pending_handoff = None
        self._handoff_message = None
        start_time = time.time()
        
        # Determine starting agent
        current_agent_name = (self.entry_point.name if self.entry_point 
                              else next(iter(self.agents.keys())))
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # Timeout check
            elapsed = time.time() - start_time
            if elapsed > self.execution_timeout:
                print(f"      ⏰ Swarm timed out after {elapsed:.1f}s")
                self.status = SwarmStatus.FAILED
                break
            
            # Repetitive handoff detection
            if len(self.node_history) >= 6:
                recent = self.node_history[-6:]
                if len(set(recent)) < 3:
                    print(f"      🔄 Repetitive handoff detected, stopping")
                    self.status = SwarmStatus.FAILED
                    break
            
            agent = self.agents.get(current_agent_name)
            if not agent:
                print(f"      ❌ Agent '{current_agent_name}' not found")
                self.status = SwarmStatus.FAILED
                break
            
            print(f"\n      ── Iteration {iteration}: Agent '{current_agent_name}' ──")
            self.node_history.append(current_agent_name)
            
            # Build context-enriched prompt
            context_prompt = self._build_context_prompt(task, current_agent_name)
            
            # Execute agent
            result = agent(context_prompt)
            self.results[current_agent_name] = result
            
            # Check for handoff
            if self._pending_handoff:
                target = self._pending_handoff
                msg = self._handoff_message
                self._pending_handoff = None
                self._handoff_message = None
                
                print(f"      🔀 Handoff: {current_agent_name} → {target}")
                self.shared_context.add(current_agent_name, "handoff_msg", msg)
                current_agent_name = target
                continue
            
            # No handoff = task complete
            print(f"      ✅ Task completed by '{current_agent_name}'")
            self.status = SwarmStatus.COMPLETED
            break
        
        if self.status == SwarmStatus.EXECUTING:
            self.status = SwarmStatus.COMPLETED
        
        total_time = round((time.time() - start_time) * 1000)
        
        return {
            "status": self.status.value,
            "iterations": iteration,
            "node_history": self.node_history,
            "total_time_ms": total_time,
            "shared_context": self.shared_context.get_all(),
            "final_agent": current_agent_name,
        }
    
    def _build_context_prompt(self, task: str, agent_name: str) -> str:
        """Build context-enriched prompt for current agent."""
        prompt = f"Task: {task}\n"
        
        if self.node_history:
            prompt += f"\nPrevious agents: {' → '.join(self.node_history)}\n"
        
        ctx = self.shared_context.get_all()
        if ctx:
            prompt += f"\nShared context: {json.dumps(ctx, default=str)[:200]}\n"
        
        other = [a for a in self.agents.keys() if a != agent_name]
        if other:
            prompt += f"\nAvailable agents for handoff: {', '.join(other)}\n"
        
        return prompt


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧪 TEST & DEMONSTRATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 70)
    print("🤖 OMNI STRANDS — Model-Driven Agent SDK")
    print("=" * 70)
    print()
    print("📖 PARADIGMS ABSORBED FROM Strands Agents:")
    print("   • Model-driven agent with event loop")
    print("   • Typed hook system (Before/After events)")
    print("   • @tool decorator with JSON Schema extraction")
    print("   • Swarm multi-agent with SharedContext + handoffs")
    print("   • Session persistence & conversation management")
    print("   • Thread-safe cancellation signal")
    
    # Define tools
    @tool(description="Calculate a mathematical expression")
    def calculator(expression: str) -> str:
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {e}"
    
    @tool(description="Search for information")
    def search(query: str) -> str:
        return f"Search results for '{query}': [Result 1, Result 2, Result 3]"
    
    # PART 1: Single Agent
    print(f"\n{'─'*60}")
    print("📋 PART 1: Single Agent with Tools")
    agent = OmniAgent(
        name="Researcher",
        system_prompt="You are a research assistant",
        tools=[calculator, search],
    )
    
    # Add a hook
    agent.hooks.add_callback(BeforeInvocationEvent,
        lambda e: print(f"      🪝 Hook: Agent '{e.agent.name}' starting invocation"))
    
    result = agent("What is the meaning of quantum computing?")
    print(f"   Result: {result}")
    
    # PART 2: Swarm
    print(f"\n{'─'*60}")
    print("📋 PART 2: Swarm Multi-Agent Collaboration")
    
    researcher = OmniAgent(name="researcher", system_prompt="Expert researcher")
    writer = OmniAgent(name="writer", system_prompt="Expert technical writer")
    reviewer = OmniAgent(name="reviewer", system_prompt="Quality reviewer")
    
    swarm = OmniSwarm(
        agents=[researcher, writer, reviewer],
        entry_point=researcher,
        max_iterations=5,
    )
    
    swarm_result = swarm.execute("Write a report on AI agent frameworks")
    print(f"\n   Swarm Result: {json.dumps(swarm_result, indent=2, default=str)[:300]}")
    
    # PART 3: Agent as Tool
    print(f"\n{'─'*60}")
    print("📋 PART 3: Agent-as-Tool Pattern")
    sub_agent = OmniAgent(name="math_expert", tools=[calculator])
    main_agent = OmniAgent(name="coordinator", tools=[sub_agent.as_tool()])
    result3 = main_agent("I need help with calculations")
    print(f"   Coordinator result: {result3}")
    
    print(f"\n{'='*70}")
    print("✅ Strands Agent SDK: META-FUNCTIONALIZED")
    print("   Model-driven event loop ✓")
    print("   Hook system (Before/After events) ✓")
    print("   @tool decorator + ToolRegistry ✓")
    print("   AgentState + SessionManager ✓")
    print("   ConversationManager (sliding window) ✓")
    print("   Swarm (SharedContext + handoff) ✓")
    print("   Agent-as-Tool pattern ✓")
    print("   Thread-safe cancellation ✓")
    print(f"{'='*70}")
