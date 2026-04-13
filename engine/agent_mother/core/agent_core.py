import time
import uuid
import json
import hashlib
from enum import Enum
from collections import defaultdict

# ==========================================
# 🤖 AGENT MOTHER: Agent Designer + Engine + Garden
# ==========================================
#
# PROSES BELAJAR JUJUR — VERTEX AI AGENT BUILDER:
# ────────────────────────────────────────────────
#
# 1. AGENT DESIGNER — Visual builder untuk merancang agent
#    ┌─────────────────────────────────────────────────┐
#    │ CARA KERJA:                                      │
#    │ - Drag-and-drop FLOW editor (seperti Dialogflow) │
#    │ - Define: Goal, Instructions, Tools, Handoffs    │
#    │ - Agent punya PERSONA (system prompt)            │
#    │ - Agent punya TOOLS (function calling)           │
#    │ - Agent punya MEMORY (session state)             │
#    │ - Multi-agent: Agent bisa HANDOFF ke agent lain  │
#    │                                                   │
#    │ KONSEP KUNCI:                                     │
#    │ - Agent = Goal + Instructions + Tools + Guardrails│
#    │ - Playbook = instruction set (if-then-else logic) │
#    │ - Flow = deterministic path (state machine)       │
#    │ - Generator = free-form LLM response             │
#    └─────────────────────────────────────────────────┘
#
# 2. AGENT ENGINE — Runtime yang menjalankan agent
#    ┌─────────────────────────────────────────────────┐
#    │ CARA KERJA:                                      │
#    │ - Menerima user input                            │
#    │ - Orchestrator LOOP: Think → Act → Observe       │
#    │   (ReAct pattern)                                │
#    │ - Think: LLM reasoning (apa yang harus dilakukan)│
#    │ - Act: panggil Tool / generate response          │
#    │ - Observe: lihat hasil Tool                      │
#    │ - Loop sampai jawaban final                      │
#    │                                                   │
#    │ ARSITEKTUR INTERNAL:                              │
#    │ - Session Manager: track conversation state       │
#    │ - Tool Executor: jalankan function calls          │
#    │ - Memory: short-term (context) + long-term (DB)  │
#    │ - Guardrails: input/output safety filters        │
#    │ - Callback Hooks: logging, tracing, evaluation   │
#    └─────────────────────────────────────────────────┘
#
# 3. AGENT GARDEN — Marketplace / Gallery agent templates
#    ┌─────────────────────────────────────────────────┐
#    │ CARA KERJA:                                      │
#    │ - Pre-built agent templates siap pakai           │
#    │ - Kategori: Customer Service, Code Review,       │
#    │   Data Analysis, Content Creation, etc.          │
#    │ - Clone, customize, deploy dalam menit           │
#    │ - Community contributions + Google official       │
#    │ - Version control + rollback                     │
#    └─────────────────────────────────────────────────┘

# ─────────────────────────────────────────────────
# BUILDING BLOCKS
# ─────────────────────────────────────────────────

class AgentType(Enum):
    PLAYBOOK = "playbook"      # Instruction-based (if-then)
    FLOW = "flow"              # Deterministic state machine
    GENERATOR = "generator"    # Free-form LLM

class ToolType(Enum):
    FUNCTION = "function"          # Python function
    API = "api"                    # REST API endpoint
    DATASTORE = "datastore"        # RAG knowledge base
    CODE_INTERPRETER = "code"      # Execute code

class GuardrailAction(Enum):
    BLOCK = "block"
    WARN = "warn"
    REWRITE = "rewrite"


# ─────────────────────────────────────────────────
# KOMPONEN 1: Tool Definition
# ─────────────────────────────────────────────────
class ToolDefinition:
    """
    PELAJARAN: Tool = fungsi yang bisa dipanggil agent.
    Vertex AI menggunakan OpenAPI spec + Function Calling.
    Tool punya: name, description, parameters (JSON Schema).
    LLM membaca description untuk MEMUTUSKAN kapan pakai Tool.
    """
    def __init__(self, name, description, parameters=None, tool_type=ToolType.FUNCTION, fn=None):
        self.name = name
        self.description = description
        self.parameters = parameters or {}
        self.tool_type = tool_type
        self.fn = fn
        self.call_count = 0

    def execute(self, **kwargs):
        self.call_count += 1
        if self.fn:
            return self.fn(**kwargs)
        return {"result": f"[{self.name}] executed with {kwargs}"}

    def to_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }


# ─────────────────────────────────────────────────
# KOMPONEN 2: Guardrails (Safety Layer)
# ─────────────────────────────────────────────────
class Guardrail:
    """
    PELAJARAN: Guardrails = safety filters SEBELUM dan SESUDAH LLM.
    Input guardrails: cegah prompt injection, toxic input
    Output guardrails: cegah leak PII, off-topic response
    """
    def __init__(self, name, check_fn, action=GuardrailAction.BLOCK, applies_to="input"):
        self.name = name
        self.check_fn = check_fn
        self.action = action
        self.applies_to = applies_to
        self.violations = 0

    def check(self, text):
        is_safe = self.check_fn(text)
        if not is_safe:
            self.violations += 1
        return is_safe


class GuardrailSuite:
    def __init__(self):
        self.input_guardrails = []
        self.output_guardrails = []

    def add(self, guardrail):
        if guardrail.applies_to == "input":
            self.input_guardrails.append(guardrail)
        else:
            self.output_guardrails.append(guardrail)

    def check_input(self, text):
        for g in self.input_guardrails:
            if not g.check(text):
                return False, g.name
        return True, None

    def check_output(self, text):
        for g in self.output_guardrails:
            if not g.check(text):
                return False, g.name
        return True, None


# ─────────────────────────────────────────────────
# KOMPONEN 3: Agent Memory
# ─────────────────────────────────────────────────
class AgentMemory:
    """
    PELAJARAN: Agent memory = 3 level:
    1. Working memory: current conversation context
    2. Short-term: session state (user preferences, slots filled)
    3. Long-term: persistent facts across sessions (DB/vector store)
    """
    def __init__(self):
        self.working = []       # Current turn messages
        self.short_term = {}    # Session-level state
        self.long_term = {}     # Cross-session facts

    def add_message(self, role, content):
        self.working.append({"role": role, "content": content, "ts": time.time()})

    def get_context(self, max_messages=10):
        return self.working[-max_messages:]

    def set_slot(self, key, value):
        self.short_term[key] = value

    def get_slot(self, key, default=None):
        return self.short_term.get(key, default)

    def remember(self, key, value):
        self.long_term[key] = {"value": value, "ts": time.time()}

    def recall(self, key):
        fact = self.long_term.get(key)
        return fact["value"] if fact else None


# ─────────────────────────────────────────────────
# KOMPONEN 4: Agent Definition (Agent Designer)
# ─────────────────────────────────────────────────
class AgentDefinition:
    """
    PELAJARAN: Agent Designer output = AgentDefinition.
    Ini adalah "blueprint" yang Agent Engine jalankan.
    """
    def __init__(self, name, goal, instructions, model="gemini-2.0-flash",
                 agent_type=AgentType.PLAYBOOK):
        self.agent_id = str(uuid.uuid4())[:8]
        self.name = name
        self.goal = goal
        self.instructions = instructions  # List of instruction strings
        self.model = model
        self.agent_type = agent_type
        self.tools = []
        self.guardrails = GuardrailSuite()
        self.sub_agents = {}  # For multi-agent handoff
        self.version = "1.0.0"
        self.created_at = time.time()

    def add_tool(self, tool):
        self.tools.append(tool)

    def add_guardrail(self, guardrail):
        self.guardrails.add(guardrail)

    def add_sub_agent(self, name, agent_def):
        self.sub_agents[name] = agent_def

    def to_manifest(self):
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "goal": self.goal,
            "model": self.model,
            "type": self.agent_type.value,
            "tools": [t.name for t in self.tools],
            "sub_agents": list(self.sub_agents.keys()),
            "version": self.version,
        }


# ─────────────────────────────────────────────────
# KOMPONEN 5: Agent Engine (ReAct Runtime)
# ─────────────────────────────────────────────────
class AgentEngine:
    """
    PELAJARAN KUNCI — ReAct Loop:
    ┌──────────────────────────────────────────┐
    │ User Input                               │
    │     ↓                                    │
    │ [THINK] LLM decides next action          │
    │     ↓                                    │
    │ [ACT] Execute tool OR generate response  │
    │     ↓                                    │
    │ [OBSERVE] Get tool result                │
    │     ↓                                    │
    │ Loop back to THINK (if more steps needed)│
    │     ↓                                    │
    │ Final Response to user                   │
    └──────────────────────────────────────────┘
    """
    def __init__(self, agent_def):
        self.agent_def = agent_def
        self.memory = AgentMemory()
        self.session_id = str(uuid.uuid4())[:8]
        self.step_count = 0
        self.trace = []  # Full execution trace
        self.callbacks = []

    def add_callback(self, fn):
        self.callbacks.append(fn)

    def _emit(self, event_type, data):
        for cb in self.callbacks:
            cb(event_type, data)
        self.trace.append({"step": self.step_count, "event": event_type, **data})

    def _think(self, user_input):
        """LLM reasoning: decide what to do next."""
        self.step_count += 1
        context = self.memory.get_context()
        available_tools = [t.name for t in self.agent_def.tools]

        # Simulate LLM reasoning
        thought = f"User asks: '{user_input[:50]}'. "
        tool_to_use = None

        for tool in self.agent_def.tools:
            keywords = tool.description.lower().split()[:5]
            if any(kw in user_input.lower() for kw in keywords if len(kw) > 3):
                tool_to_use = tool
                thought += f"I should use tool '{tool.name}'."
                break

        if not tool_to_use:
            # Check sub-agents for handoff
            for sub_name, sub_agent in self.agent_def.sub_agents.items():
                sub_keywords = sub_agent.goal.lower().split()[:5]
                if any(kw in user_input.lower() for kw in sub_keywords if len(kw) > 3):
                    thought += f"I should handoff to '{sub_name}'."
                    self._emit("HANDOFF", {"to": sub_name, "thought": thought})
                    return {"action": "handoff", "target": sub_name, "thought": thought}

            thought += "I can answer directly from my knowledge."

        self._emit("THINK", {"thought": thought, "tool": tool_to_use.name if tool_to_use else None})
        return {"action": "tool" if tool_to_use else "respond", "tool": tool_to_use, "thought": thought}

    def _act(self, decision, user_input):
        """Execute tool or generate response."""
        if decision["action"] == "tool":
            tool = decision["tool"]
            result = tool.execute(query=user_input)
            self._emit("ACT", {"tool": tool.name, "result": str(result)[:100]})
            return result
        elif decision["action"] == "handoff":
            target = decision["target"]
            sub_agent = self.agent_def.sub_agents[target]
            sub_engine = AgentEngine(sub_agent)
            return sub_engine.run(user_input)
        else:
            # Direct response generation
            response = self._generate_response(user_input)
            self._emit("ACT", {"type": "generate", "response": response[:100]})
            return {"response": response}

    def _observe(self, action_result):
        """Process tool result."""
        self._emit("OBSERVE", {"result": str(action_result)[:100]})
        return action_result

    def _generate_response(self, user_input):
        """Simulate LLM generation based on agent persona."""
        instructions = "; ".join(self.agent_def.instructions[:3])
        return f"[{self.agent_def.name}] Berdasarkan instruksi saya ({instructions[:60]}...), " \
               f"jawaban untuk '{user_input[:40]}' adalah: [Generated Response]"

    def run(self, user_input, max_steps=5):
        """Main execution loop."""
        print(f"\n      🤖 [{self.agent_def.name}] Session: {self.session_id}")

        # Input guardrails
        safe, violation = self.agent_def.guardrails.check_input(user_input)
        if not safe:
            print(f"         🛡️ INPUT BLOCKED: {violation}")
            return {"response": f"Input ditolak oleh guardrail: {violation}", "blocked": True}

        self.memory.add_message("user", user_input)

        # ReAct Loop
        for step in range(max_steps):
            decision = self._think(user_input)
            print(f"         💭 Think: {decision['thought'][:60]}...")

            result = self._act(decision, user_input)

            if decision["action"] == "respond" or decision["action"] == "handoff":
                response = result.get("response", str(result))
                break
            else:
                observation = self._observe(result)
                print(f"         👁  Observe: {str(observation)[:60]}...")
                response = f"Tool result: {observation}"
                break  # Simplified: 1-step for demo

        # Output guardrails
        safe, violation = self.agent_def.guardrails.check_output(response)
        if not safe:
            response = f"[Output filtered by {violation}]"
            print(f"         🛡️ OUTPUT FILTERED: {violation}")

        self.memory.add_message("assistant", response)
        print(f"         💬 Response: {response[:60]}...")
        return {"response": response, "steps": self.step_count, "session": self.session_id}


# ─────────────────────────────────────────────────
# KOMPONEN 6: Agent Garden (Template Registry)
# ─────────────────────────────────────────────────
class AgentGarden:
    """
    PELAJARAN: Agent Garden = marketplace of pre-built agents.
    - Official templates (Google): Customer Service, Code Gen
    - Community templates: domain-specific agents
    - Clone → Customize → Deploy pipeline
    """
    def __init__(self):
        self.templates = {}
        self.categories = defaultdict(list)
        self.deployments = []

    def register_template(self, agent_def, category, description, author="official"):
        template = {
            "agent_def": agent_def,
            "category": category,
            "description": description,
            "author": author,
            "downloads": 0,
            "rating": 0.0,
            "created_at": time.time(),
        }
        self.templates[agent_def.name] = template
        self.categories[category].append(agent_def.name)

    def browse(self, category=None):
        if category:
            return [(name, self.templates[name]["description"])
                    for name in self.categories.get(category, [])]
        return [(name, t["description"]) for name, t in self.templates.items()]

    def clone(self, template_name, new_name):
        """Clone template for customization."""
        if template_name not in self.templates:
            return None
        original = self.templates[template_name]["agent_def"]
        clone = AgentDefinition(
            new_name, original.goal, list(original.instructions),
            original.model, original.agent_type
        )
        for tool in original.tools:
            clone.add_tool(tool)
        self.templates[template_name]["downloads"] += 1
        return clone

    def deploy(self, agent_def, environment="staging"):
        deployment = {
            "agent": agent_def.name,
            "environment": environment,
            "endpoint": f"https://agent-{agent_def.agent_id}.run.app",
            "deployed_at": time.time(),
            "status": "RUNNING",
        }
        self.deployments.append(deployment)
        return deployment


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("🤖 AGENT MOTHER: Agent Designer + Engine + Garden")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN:")
    print("   Agent Designer: Goal + Instructions + Tools + Guardrails → Blueprint")
    print("   Agent Engine: ReAct Loop (Think → Act → Observe → Respond)")
    print("   Agent Garden: Template marketplace (browse → clone → deploy)")

    # ── PART 1: Design Agents ──
    print(f"\n{'─'*60}")
    print("📋 PART 1: Agent Designer — Define 3 Agents")

    # Agent 1: Customer Service
    cs_agent = AgentDefinition(
        "CustomerServiceBot",
        "Membantu pelanggan dengan pertanyaan tentang produk dan order",
        [
            "Selalu sapa pelanggan dengan ramah",
            "Cari informasi order di database sebelum menjawab",
            "Jika tidak bisa bantu, eskalasi ke human agent",
            "Jangan pernah memberi diskon tanpa approval manager",
        ],
        model="gemini-2.0-flash",
        agent_type=AgentType.PLAYBOOK,
    )
    cs_agent.add_tool(ToolDefinition(
        "lookup_order", "Cari status order berdasarkan order ID",
        {"type": "object", "properties": {"order_id": {"type": "string"}}},
        fn=lambda **kw: {"order_id": kw.get("query", "ORD-?"), "status": "shipped", "eta": "2 hari"}
    ))
    cs_agent.add_tool(ToolDefinition(
        "search_faq", "Cari FAQ berdasarkan pertanyaan pelanggan",
        fn=lambda **kw: {"answer": f"FAQ untuk: {kw.get('query', '?')[:30]}", "confidence": 0.85}
    ))
    cs_agent.add_guardrail(Guardrail(
        "no_profanity", lambda t: "bodoh" not in t.lower() and "jelek" not in t.lower(),
        applies_to="input"
    ))
    cs_agent.add_guardrail(Guardrail(
        "no_pii_leak", lambda t: "SSN" not in t and "credit card" not in t.lower(),
        applies_to="output"
    ))
    print(f"   Agent 1: {json.dumps(cs_agent.to_manifest(), indent=2)}")

    # Agent 2: Code Review
    code_agent = AgentDefinition(
        "CodeReviewBot",
        "Review kode Python/JavaScript dan berikan feedback",
        [
            "Periksa coding standards (PEP8 / ESLint)",
            "Identifikasi bug potensial dan security vulnerabilities",
            "Sarankan improvement untuk performance",
            "Berikan score 1-10 untuk code quality",
        ],
        agent_type=AgentType.GENERATOR,
    )
    code_agent.add_tool(ToolDefinition(
        "run_linter", "Jalankan linter pada kode",
        fn=lambda **kw: {"issues": 3, "warnings": 5, "errors": 0}
    ))

    # Agent 3: Data Analyst
    data_agent = AgentDefinition(
        "DataAnalystBot",
        "Analisis data, buat visualisasi, dan generate insight",
        ["Query database SQL", "Buat chart dari hasil query", "Summarize trends"],
        agent_type=AgentType.FLOW,
    )
    data_agent.add_tool(ToolDefinition(
        "query_database", "Jalankan SQL query di database",
        fn=lambda **kw: {"rows": 42, "columns": ["id", "revenue", "date"]}
    ))

    # Multi-agent: CS Agent bisa handoff ke Code dan Data agents
    cs_agent.add_sub_agent("code_review", code_agent)
    cs_agent.add_sub_agent("data_analysis", data_agent)

    print(f"   Agent 2: {code_agent.name} ({code_agent.agent_type.value})")
    print(f"   Agent 3: {data_agent.name} ({data_agent.agent_type.value})")
    print(f"   Multi-agent: {cs_agent.name} can handoff to {list(cs_agent.sub_agents.keys())}")

    # ── PART 2: Agent Engine ──
    print(f"\n{'─'*60}")
    print("📋 PART 2: Agent Engine — ReAct Loop")

    engine = AgentEngine(cs_agent)

    # Test 1: Normal query → tool use
    print("\n   [Test 1: Tool Use]")
    result = engine.run("Dimana order saya ORD-12345?")

    # Test 2: Handoff ke sub-agent
    print("\n   [Test 2: Sub-agent Handoff]")
    result = engine.run("Review kode Python ini untuk bugs")

    # Test 3: Guardrail block
    print("\n   [Test 3: Input Guardrail]")
    result = engine.run("Produk kalian bodoh dan jelek!")

    # Test 4: Direct response
    print("\n   [Test 4: Direct Response]")
    result = engine.run("Terima kasih atas bantuannya!")

    # ── PART 3: Agent Garden ──
    print(f"\n{'─'*60}")
    print("📋 PART 3: Agent Garden — Template Marketplace")
    garden = AgentGarden()

    garden.register_template(cs_agent, "customer_service", "Bot CS lengkap dengan FAQ dan order lookup")
    garden.register_template(code_agent, "developer_tools", "Code reviewer dengan linter integration")
    garden.register_template(data_agent, "analytics", "Data analyst dengan SQL query capability")

    print("\n   📂 Browse All Templates:")
    for name, desc in garden.browse():
        print(f"      🌱 {name}: {desc}")

    print("\n   📂 Developer Tools Category:")
    for name, desc in garden.browse("developer_tools"):
        print(f"      🌱 {name}: {desc}")

    # Clone and customize
    my_bot = garden.clone("CustomerServiceBot", "MyCustomCSBot")
    print(f"\n   📋 Cloned: {my_bot.name} (from CustomerServiceBot)")
    my_bot.instructions.append("Selalu gunakan bahasa Indonesia formal")

    # Deploy
    deployment = garden.deploy(my_bot, "production")
    print(f"   🚀 Deployed: {deployment['endpoint']} ({deployment['status']})")

    # ── PART 4: Memory System ──
    print(f"\n{'─'*60}")
    print("📋 PART 4: Agent Memory (3 levels)")
    mem = engine.memory
    mem.set_slot("user_name", "Ikky")
    mem.set_slot("preferred_language", "id")
    mem.remember("past_order_count", 15)
    mem.remember("loyalty_tier", "Gold")

    print(f"   Working memory: {len(mem.working)} messages")
    print(f"   Short-term: {mem.short_term}")
    print(f"   Long-term: user_name={mem.recall('past_order_count')}, tier={mem.recall('loyalty_tier')}")

    # ── Summary ──
    print(f"\n{'='*70}")
    print("✅ Agent Designer + Engine + Garden: DIPELAJARI MENDALAM.")
    print("   Agent Designer: Goal + Instructions + Tools + Guardrails ✓")
    print("   Agent Types: Playbook / Flow / Generator ✓")
    print("   Tool Definition: function, api, datastore, code_interpreter ✓")
    print("   Guardrails: input/output safety (block/warn/rewrite) ✓")
    print("   Agent Engine: ReAct loop (Think → Act → Observe) ✓")
    print("   Multi-Agent: Handoff to sub-agents ✓")
    print("   Agent Memory: working + short-term + long-term ✓")
    print("   Agent Garden: browse → clone → customize → deploy ✓")
    print(f"{'='*70}")
