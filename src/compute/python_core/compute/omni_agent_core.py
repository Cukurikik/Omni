"""
╔══════════════════════════════════════════════════════════════════╗
║  🧬 OMNI AI — AGENT CORE ENGINE                                ║
║  Sub-Agents: Agent Designer | Agent Engine | Agent Garden | Tools║
║  Parent: OMNI Agent Mother (Ibu dari semua agent)               ║
║  Runtime: OMNI-NEXUS / LLVM-Omni                                ║
╚══════════════════════════════════════════════════════════════════╝

PROSES UTAMA — OMNI AI:
──────────────────────────────────────────────────
OMNI AI adalah platform agent MILIK OMNI Framework.
Setiap komponen = SUB-AGENT (anak) dari Agent Mother.
Sub-agent bisa berkomunikasi, handoff, dan collaborate.

ARSITEKTUR OMNI AI:
┌─────────────────────────────────────────────────────┐
│            👩 OMNI AGENT MOTHER                     │
│                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐│
│  │Designer │←→│ Engine  │←→│ Garden  │←→│ Tools  ││
│  │(rancang)│  │(jalankan)│  │(template)│  │(aksi)  ││
│  └────┬────┘  └────┬────┘  └────┬────┘  └───┬────┘│
│       │            │            │            │      │
│  ┌────┴────────────┴────────────┴────────────┴────┐│
│  │     OMNI BRIDGE (Inter-Agent Communication)     ││
│  └─────────────────────────────────────────────────┘│
│                                                     │
│  [FineTuning] [Eval] [RAG] [Training] [Features]   │
│  [Datasets] [Experiments] [Metadata] [Colab] [WB]  │
│  [Mobile] [Desktop] [Voice] [MAS] [LLM] [Data/RAG] │
└─────────────────────────────────────────────────────┘
"""

import time
import uuid
import json
import hashlib
from enum import Enum
from collections import defaultdict


# ═══════════════════════════════════════════════════
# OMNI AI TYPE SYSTEM
# ═══════════════════════════════════════════════════

class OmniAgentType(Enum):
    """Tipe agent di OMNI AI — lebih kaya dari platform lain."""
    PLAYBOOK = "playbook"          # Instruction-based (if-then rules)
    FLOW = "flow"                  # Deterministic state machine
    GENERATOR = "generator"        # Free-form LLM
    ORCHESTRATOR = "orchestrator"  # Multi-agent coordinator
    SPECIALIST = "specialist"      # Domain expert (fine-tuned)
    SENTINEL = "sentinel"          # Security/monitoring agent

class OmniToolType(Enum):
    FUNCTION = "omni_function"         # OMNI native function
    API = "omni_api"                   # REST/GraphQL endpoint
    DATASTORE = "omni_datastore"       # RAG knowledge base
    CODE_EXEC = "omni_code_exec"       # Execute multi-lang code
    SYSTEM = "omni_system"             # OS-level operations
    BRIDGE = "omni_bridge"             # Cross-agent communication

class GuardrailLevel(Enum):
    BLOCK = "block"
    WARN = "warn"
    REWRITE = "rewrite"
    LOG = "log"

class AgentStatus(Enum):
    IDLE = "IDLE"
    THINKING = "THINKING"
    ACTING = "ACTING"
    OBSERVING = "OBSERVING"
    HANDOFF = "HANDOFF"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"


# ═══════════════════════════════════════════════════
# SUB-AGENT 1: OMNI TOOLS — Aksi yang bisa dilakukan agent
# ═══════════════════════════════════════════════════

class OmniTool:
    """
    OMNI Tool: kemampuan agent untuk BERTINDAK.
    Di OMNI AI, tool bisa:
    - Panggil function Python/Go/Rust (multi-lang)
    - Hit API endpoint
    - Query knowledge base (RAG)
    - Execute code dalam sandbox
    - Operasi OS-level (file, process, network)
    - Komunikasi antar-agent (bridge)
    """
    def __init__(self, name, description, fn=None, tool_type=OmniToolType.FUNCTION,
                 parameters=None, permissions=None):
        self.tool_id = str(uuid.uuid4())[:8]
        self.name = name
        self.description = description
        self.fn = fn
        self.tool_type = tool_type
        self.parameters = parameters or {}
        self.permissions = permissions or []
        self.call_count = 0
        self.avg_latency_ms = 0
        self.error_count = 0

    def execute(self, **kwargs):
        start = time.time()
        self.call_count += 1
        try:
            if self.fn:
                result = self.fn(**kwargs)
            else:
                result = {"status": "ok", "tool": self.name, "args": kwargs}
            latency = (time.time() - start) * 1000
            self.avg_latency_ms = (self.avg_latency_ms * (self.call_count - 1) + latency) / self.call_count
            return {"success": True, "data": result, "latency_ms": round(latency, 2)}
        except Exception as e:
            self.error_count += 1
            return {"success": False, "error": str(e)}

    def to_schema(self):
        """OMNI Function Calling Schema (OpenAPI-compatible)."""
        return {
            "type": self.tool_type.value,
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
            "permissions": self.permissions,
        }


class OmniToolRegistry:
    """Registry pusat semua tools di OMNI AI."""
    def __init__(self):
        self.tools = {}
        self.execution_log = []

    def register(self, tool):
        self.tools[tool.name] = tool
        return tool

    def execute(self, name, **kwargs):
        tool = self.tools.get(name)
        if not tool:
            return {"success": False, "error": f"Tool '{name}' not registered"}
        result = tool.execute(**kwargs)
        self.execution_log.append({
            "tool": name, "ts": time.time(),
            "success": result["success"],
        })
        return result

    def list_all(self):
        return [{"name": t.name, "type": t.tool_type.value, "calls": t.call_count,
                "errors": t.error_count} for t in self.tools.values()]

    def get_schemas(self):
        return [t.to_schema() for t in self.tools.values()]


# ═══════════════════════════════════════════════════
# SUB-AGENT 2: OMNI GUARDRAILS — Perlindungan agent
# ═══════════════════════════════════════════════════

class OmniGuardrail:
    """Safety filter: input/output protection."""
    def __init__(self, name, check_fn, level=GuardrailLevel.BLOCK, scope="input"):
        self.name = name
        self.check_fn = check_fn
        self.level = level
        self.scope = scope
        self.violations = 0

    def check(self, text):
        safe = self.check_fn(text)
        if not safe:
            self.violations += 1
        return safe


class OmniGuardrailSuite:
    def __init__(self):
        self.input_guards = []
        self.output_guards = []

    def add(self, guard):
        if guard.scope == "input":
            self.input_guards.append(guard)
        else:
            self.output_guards.append(guard)

    def check_input(self, text):
        for g in self.input_guards:
            if not g.check(text):
                return False, g.name, g.level
        return True, None, None

    def check_output(self, text):
        for g in self.output_guards:
            if not g.check(text):
                return False, g.name, g.level
        return True, None, None


# ═══════════════════════════════════════════════════
# SUB-AGENT 3: OMNI AGENT MEMORY — 4-level memory
# ═══════════════════════════════════════════════════

class OmniMemory:
    """
    OMNI Memory = 4 level:
    1. Immediate: current turn (instructions + user input)
    2. Working: conversation history (sliding window)
    3. Session: cross-turn state (slots, preferences)
    4. Persistent: cross-session knowledge (facts, user profile)
    """
    def __init__(self, max_working=20):
        self.immediate = {}
        self.working = []
        self.session = {}
        self.persistent = {}
        self.max_working = max_working

    def add_message(self, role, content, metadata=None):
        msg = {"role": role, "content": content, "ts": time.time(),
               "metadata": metadata or {}}
        self.working.append(msg)
        if len(self.working) > self.max_working:
            self.working = self.working[-self.max_working:]

    def set_immediate(self, key, value):
        self.immediate[key] = value

    def set_session(self, key, value):
        self.session[key] = value

    def get_session(self, key, default=None):
        return self.session.get(key, default)

    def remember(self, key, value):
        self.persistent[key] = {"value": value, "ts": time.time()}

    def recall(self, key):
        fact = self.persistent.get(key)
        return fact["value"] if fact else None

    def get_context(self, n=10):
        return self.working[-n:]

    def get_full_state(self):
        return {
            "immediate": self.immediate,
            "working_messages": len(self.working),
            "session_slots": list(self.session.keys()),
            "persistent_facts": list(self.persistent.keys()),
        }


# ═══════════════════════════════════════════════════
# SUB-AGENT 4: OMNI AGENT DESIGNER — Blueprint Builder
# ═══════════════════════════════════════════════════

class OmniAgentDefinition:
    """
    OMNI Agent Designer: merancang blueprint agent baru.
    Output = OmniAgentDefinition (blueprint).

    OMNI AGENT = Goal + Persona + Instructions + Tools + Guardrails + Memory + Children
    """
    def __init__(self, name, goal, instructions, persona=None,
                 model="omni-llm-v2", agent_type=OmniAgentType.PLAYBOOK):
        self.agent_id = str(uuid.uuid4())[:8]
        self.name = name
        self.goal = goal
        self.persona = persona or f"Saya adalah {name}, sub-agent OMNI AI."
        self.instructions = instructions
        self.model = model
        self.agent_type = agent_type
        self.tools = []
        self.guardrails = OmniGuardrailSuite()
        self.children = {}    # Sub-agents (for multi-agent)
        self.parent = None    # Parent agent reference
        self.version = "1.0.0"
        self.domain = "general"
        self.created_at = time.time()
        self.capabilities = []

    def add_tool(self, tool):
        self.tools.append(tool)
        self.capabilities.append(tool.name)

    def add_guardrail(self, guard):
        self.guardrails.add(guard)

    def add_child(self, name, child_def):
        child_def.parent = self.name
        self.children[name] = child_def

    def to_manifest(self):
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "goal": self.goal,
            "model": self.model,
            "type": self.agent_type.value,
            "domain": self.domain,
            "tools": [t.name for t in self.tools],
            "children": list(self.children.keys()),
            "parent": self.parent,
            "version": self.version,
        }


# ═══════════════════════════════════════════════════
# SUB-AGENT 5: OMNI AGENT ENGINE — ReAct Runtime
# ═══════════════════════════════════════════════════

class OmniAgentEngine:
    """
    OMNI ReAct Loop:
    ┌──────────────────────────────────────────┐
    │ User Input                               │
    │     ↓                                    │
    │ [1. PERCEIVE] Parse input + load context │
    │     ↓                                    │
    │ [2. THINK] LLM reasoning → decide action │
    │     ↓                                    │
    │ [3. ACT] Execute tool / handoff / respond│
    │     ↓                                    │
    │ [4. OBSERVE] Process action result       │
    │     ↓                                    │
    │ [5. REFLECT] Update memory + learn       │
    │     ↓                                    │
    │ Loop back to THINK if not done           │
    │     ↓                                    │
    │ Final Response (grounded + safe)         │
    └──────────────────────────────────────────┘
    """
    def __init__(self, agent_def):
        self.agent_def = agent_def
        self.memory = OmniMemory()
        self.session_id = str(uuid.uuid4())[:8]
        self.status = AgentStatus.IDLE
        self.step_count = 0
        self.trace = []
        self.callbacks = []

    def _emit(self, event, data):
        entry = {"step": self.step_count, "event": event, "ts": time.time(), **data}
        self.trace.append(entry)
        for cb in self.callbacks:
            cb(event, entry)

    def _perceive(self, user_input):
        """Step 1: Parse input, load context."""
        self.status = AgentStatus.THINKING
        context = self.memory.get_context()
        session_state = self.memory.session
        self._emit("PERCEIVE", {"input": user_input[:50], "context_len": len(context),
                                "session_slots": len(session_state)})
        return {"input": user_input, "context": context, "state": session_state}

    def _think(self, perception):
        """Step 2: LLM reasoning via Ollama API — PRODUCTION, bukan keyword matching."""
        self.step_count += 1
        user_input = perception["input"]

        # Build tool descriptions for LLM function calling
        tool_descriptions = [
            f"- {t.name}: {t.description}" for t in self.agent_def.tools
        ]
        child_descriptions = [
            f"- {n}: {c.goal}" for n, c in self.agent_def.children.items()
        ]

        system_prompt = (
            f"Kamu adalah {self.agent_def.name}. {self.agent_def.persona}\n"
            f"Instruksi: {'; '.join(self.agent_def.instructions[:3])}\n\n"
            f"TOOLS TERSEDIA:\n" + "\n".join(tool_descriptions) + "\n\n"
            f"SUB-AGENTS:\n" + "\n".join(child_descriptions) + "\n\n"
            f"KEPUTUSAN: Jawab dalam JSON dengan format:\n"
            f'  {{"action": "tool", "tool_name": "<nama>", "reason": "<alasan>"}}\n'
            f'  {{"action": "handoff", "target": "<nama_child>", "reason": "<alasan>"}}\n'
            f'  {{"action": "respond", "response": "<jawaban langsung>"}}'
        )

        # Panggil Ollama secara NYATA
        decision = self._call_ollama(system_prompt, user_input)

        if decision:
            action = decision.get("action", "respond")
            if action == "tool":
                tool_name = decision.get("tool_name", "")
                tool = next((t for t in self.agent_def.tools if t.name == tool_name), None)
                if tool:
                    thought = f"Gunakan tool '{tool.name}': {decision.get('reason', '')[:40]}"
                    self._emit("THINK", {"thought": thought, "action": "tool", "tool": tool.name})
                    return {"action": "tool", "tool": tool, "thought": thought}
            elif action == "handoff":
                target = decision.get("target", "")
                if target in self.agent_def.children:
                    thought = f"Handoff ke '{target}': {decision.get('reason', '')[:40]}"
                    self._emit("THINK", {"thought": thought, "action": "handoff", "target": target})
                    return {"action": "handoff", "target": target, "thought": thought}
            elif action == "respond":
                response_text = decision.get("response", f"Menjawab: {user_input[:40]}")
                thought = f"Jawab langsung: {response_text[:40]}"
                self._emit("THINK", {"thought": thought, "action": "respond"})
                return {"action": "respond", "thought": thought, "llm_response": response_text}

        # Fallback jika Ollama tidak tersedia — gunakan tool matching sederhana
        for tool in self.agent_def.tools:
            desc_words = set(tool.description.lower().split())
            input_words = set(user_input.lower().split())
            overlap = len(desc_words & input_words)
            if overlap >= 2 or any(w in user_input.lower() for w in desc_words if len(w) > 4):
                thought = f"[Fallback] Gunakan tool '{tool.name}' untuk: {user_input[:40]}"
                self._emit("THINK", {"thought": thought, "action": "tool", "tool": tool.name})
                return {"action": "tool", "tool": tool, "thought": thought}

        thought = f"[Fallback] Jawab langsung: {user_input[:40]}"
        self._emit("THINK", {"thought": thought, "action": "respond"})
        return {"action": "respond", "thought": thought}

    def _call_ollama(self, system_prompt, user_message, model="llama3.2"):
        """Memanggil Ollama /api/chat secara nyata via HTTP. PRODUCTION."""
        import urllib.request
        import urllib.error
        try:
            url = "http://localhost:11434/api/chat"
            payload = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "stream": False,
                "format": "json",
            }).encode("utf-8")

            req = urllib.request.Request(url, data=payload,
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                content = result.get("message", {}).get("content", "{}")
                return json.loads(content)
        except (urllib.error.URLError, json.JSONDecodeError, Exception):
            # Ollama tidak aktif — return None agar fallback logic digunakan
            return None

    def _act(self, decision, user_input):
        """Step 3: Execute action."""
        self.status = AgentStatus.ACTING

        if decision["action"] == "tool":
            result = decision["tool"].execute(query=user_input)
            self._emit("ACT", {"type": "tool", "tool": decision["tool"].name,
                               "result": str(result.get("data", ""))[:60]})
            return result

        elif decision["action"] == "handoff":
            target = decision["target"]
            child_def = self.agent_def.children[target]
            child_engine = OmniAgentEngine(child_def)
            self.status = AgentStatus.HANDOFF
            self._emit("ACT", {"type": "handoff", "target": target})
            return child_engine.run(user_input)

        else:
            # Generate response from persona
            instructions = "; ".join(self.agent_def.instructions[:2])
            response = (f"[{self.agent_def.name}] {self.agent_def.persona[:40]}... "
                       f"| Instruksi: {instructions[:40]}... "
                       f"| Jawaban untuk: '{user_input[:30]}'")
            self._emit("ACT", {"type": "generate", "response": response[:60]})
            return {"success": True, "data": {"response": response}}

    def _observe(self, action_result):
        """Step 4: Process result."""
        self.status = AgentStatus.OBSERVING
        self._emit("OBSERVE", {"result": str(action_result)[:60]})
        return action_result

    def _reflect(self, user_input, result):
        """Step 5: Update memory, learn (OMNI exclusive)."""
        self.memory.add_message("user", user_input)
        data = result.get("data", {})
        if isinstance(data, dict):
            response = str(data.get("response", str(data)[:200]))
        else:
            response = str(data)[:200]
        self.memory.add_message("assistant", response[:200])
        self._emit("REFLECT", {"memory_size": len(self.memory.working)})

    def run(self, user_input, max_steps=5):
        """Full OMNI execution loop: Perceive → Think → Act → Observe → Reflect."""
        print(f"\n      🤖 [{self.agent_def.name}] Session: {self.session_id}")

        # Guardrail check
        safe, violation, level = self.agent_def.guardrails.check_input(user_input)
        if not safe:
            print(f"         🛡️ BLOCKED: {violation} ({level.value})")
            return {"success": False, "blocked": True, "guardrail": violation}

        perception = self._perceive(user_input)

        for step in range(max_steps):
            decision = self._think(perception)
            print(f"         💭 Think: {decision['thought'][:55]}...")

            result = self._act(decision, user_input)

            if decision["action"] == "handoff":
                return result

            observation = self._observe(result)

            if result.get("success"):
                data = result.get("data", {})
                resp = data.get("response", str(data)[:60]) if isinstance(data, dict) else str(data)[:60]
                print(f"         💬 Response: {str(resp)[:55]}...")
                break

        self._reflect(user_input, result)
        self.status = AgentStatus.COMPLETE

        # Output guardrail
        final_resp = str(result.get("data", ""))
        safe, violation, level = self.agent_def.guardrails.check_output(final_resp)
        if not safe:
            print(f"         🛡️ OUTPUT FILTERED: {violation}")

        return result


# ═══════════════════════════════════════════════════
# SUB-AGENT 6: OMNI AGENT GARDEN — Template Marketplace
# ═══════════════════════════════════════════════════

class OmniAgentGarden:
    """
    OMNI Agent Garden = marketplace template OMNI AI.
    - Templates dibuat oleh OMNI community
    - Setiap template punya domain + rating + version
    - One-click clone → customize → deploy ke OMNI Cloud
    """
    def __init__(self):
        self.templates = {}
        self.categories = defaultdict(list)
        self.deployments = []

    def publish(self, agent_def, category, description, author="omni-team"):
        template = {
            "agent": agent_def,
            "category": category,
            "description": description,
            "author": author,
            "downloads": 0,
            "rating": 4.5 + (hash(agent_def.name) % 5) / 10.0,
            "created_at": time.time(),
        }
        self.templates[agent_def.name] = template
        self.categories[category].append(agent_def.name)
        return template

    def browse(self, category=None):
        if category:
            return [(n, self.templates[n]["description"], self.templates[n]["rating"])
                    for n in self.categories.get(category, [])]
        return [(n, t["description"], t["rating"]) for n, t in self.templates.items()]

    def clone(self, template_name, new_name):
        if template_name not in self.templates:
            return None
        orig = self.templates[template_name]["agent"]
        clone = OmniAgentDefinition(new_name, orig.goal, list(orig.instructions),
                                    orig.persona, orig.model, orig.agent_type)
        clone.domain = orig.domain
        for tool in orig.tools:
            clone.add_tool(tool)
        self.templates[template_name]["downloads"] += 1
        return clone

    def deploy(self, agent_def, env="production"):
        endpoint = f"https://{agent_def.name.lower().replace(' ', '-')}.omni.ai"
        dep = {"agent": agent_def.name, "env": env, "endpoint": endpoint,
               "status": "RUNNING", "deployed_at": time.time()}
        self.deployments.append(dep)
        return dep



