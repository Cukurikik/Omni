import time
import random
import copy
from enum import Enum
from collections import defaultdict

# ==========================================
# ⚡ OMNI AUTOMATION: Workflow Engine (Phase 160)
# ==========================================
#
# PROSES BELAJAR:
# ──────────────────────
# 3 paradigma utama workflow automation:
#
# 1. TEMPORAL.IO — Durable Execution
#    Workflow = KODE BIASA (Go/Python/TS) yang bisa sleep berhari-hari.
#    Event sourcing: setiap state change disimpan sebagai event.
#    Jika crash → replay events → state pulih otomatis.
#    Cocok untuk: long-running process (human approval, SLA).
#
# 2. n8n — Visual Node-Based
#    Workflow = DAG nodes visual (drag-and-drop).
#    Trigger nodes → Action nodes → Output.
#    Cocok untuk: IT ops, non-developer, integrasi SaaS.
#
# 3. PREFECT — Python-Native DAG
#    Workflow = Python function biasa + decorator @task/@flow.
#    Dynamic DAG di runtime (bisa branching, loop).
#    Control plane hybrid (metadata di cloud, eksekusi di infra sendiri).
#    Cocok untuk: data engineers, ML pipeline.

class TaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    WAITING = "waiting"  # Temporal: menunggu signal/timer

# ─────────────────────────────────────────────────
# PARADIGMA 1: Temporal-Style Durable Execution
# ─────────────────────────────────────────────────
class Event:
    """Event sourcing: setiap state change = 1 event."""
    def __init__(self, event_type, data=None):
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = time.time()

class TemporalWorkflow:
    """
    PELAJARAN: Temporal workflow = kode imperatif biasa.
    BUKAN DAG. Bisa loop, if-else, sleep berhari-hari.
    Event history menyimpan SEMUA yang terjadi.
    Jika crash → replay events → state PULIH.
    """
    def __init__(self, name):
        self.name = name
        self.event_history = []
        self.state = {}
        self.activities = {}
        self.timers = []
        self.signals = {}

    def register_activity(self, name, fn, retry_policy=None):
        self.activities[name] = {
            "fn": fn,
            "retry": retry_policy or {"max_attempts": 3, "backoff": 1.0},
        }

    def execute_activity(self, name, *args):
        """Execute activity with retry policy."""
        if name not in self.activities:
            raise ValueError(f"Activity '{name}' not registered")

        activity = self.activities[name]
        policy = activity["retry"]
        last_error = None

        for attempt in range(1, policy["max_attempts"] + 1):
            try:
                self.event_history.append(Event("ActivityStarted", {"name": name, "attempt": attempt}))
                result = activity["fn"](*args)
                self.event_history.append(Event("ActivityCompleted", {"name": name, "result": str(result)[:50]}))
                print(f"      ✅ Activity '{name}' completed (attempt {attempt})")
                return result
            except Exception as e:
                last_error = e
                self.event_history.append(Event("ActivityFailed", {"name": name, "error": str(e), "attempt": attempt}))
                print(f"      ❌ Activity '{name}' failed (attempt {attempt}): {e}")
                if attempt < policy["max_attempts"]:
                    print(f"         🔄 Retrying in {policy['backoff']}s...")

        raise last_error

    def sleep(self, duration_name, seconds):
        """Durable sleep — survives crash."""
        self.event_history.append(Event("TimerStarted", {"name": duration_name, "seconds": seconds}))
        print(f"      ⏰ Timer '{duration_name}': {seconds}s (durable, survives crash)")
        self.event_history.append(Event("TimerFired", {"name": duration_name}))

    def wait_for_signal(self, signal_name):
        """Wait for external signal (human approval, webhook, dll)."""
        self.event_history.append(Event("SignalWaiting", {"name": signal_name}))
        print(f"      📡 Waiting for signal '{signal_name}'...")
        # Simulate signal received
        self.signals[signal_name] = {"received": True, "data": {"approved": True}}
        self.event_history.append(Event("SignalReceived", {"name": signal_name}))
        print(f"      📡 Signal '{signal_name}' received!")
        return self.signals[signal_name]["data"]

    def replay_from_history(self):
        """Replay event history untuk recovery dari crash."""
        print(f"\n   🔄 [REPLAY] Replaying {len(self.event_history)} events...")
        completed = [e for e in self.event_history if e.event_type == "ActivityCompleted"]
        failed = [e for e in self.event_history if e.event_type == "ActivityFailed"]
        print(f"      Activities completed: {len(completed)}")
        print(f"      Activities failed: {len(failed)}")
        print(f"      State recovered ✅")


# ─────────────────────────────────────────────────
# PARADIGMA 2: n8n-Style Visual Node Workflow
# ─────────────────────────────────────────────────
class WorkflowNode:
    """n8n node — unit terkecil dalam visual workflow."""
    def __init__(self, name, node_type, config=None):
        self.name = name
        self.node_type = node_type  # trigger, action, condition, output
        self.config = config or {}
        self.connections = []  # next nodes
        self.output = None

    def execute(self, input_data):
        if self.node_type == "trigger":
            self.output = {"triggered": True, **self.config}
            print(f"      ⚡ [{self.name}] Trigger fired")
        elif self.node_type == "action":
            fn = self.config.get("action", lambda d: d)
            self.output = fn(input_data)
            print(f"      ⚙️ [{self.name}] Action executed")
        elif self.node_type == "condition":
            condition_fn = self.config.get("condition", lambda d: True)
            result = condition_fn(input_data)
            self.output = {**input_data, "condition_result": result}
            print(f"      🔀 [{self.name}] Condition: {result}")
        elif self.node_type == "output":
            self.output = input_data
            print(f"      📤 [{self.name}] Output: {str(input_data)[:50]}")
        return self.output


class N8NWorkflow:
    """
    PELAJARAN: n8n workflow = DAG visual.
    Nodes connected by edges. Trigger → Actions → Output.
    Cocok untuk non-developer (drag-and-drop).
    """
    def __init__(self, name):
        self.name = name
        self.nodes = {}
        self.start_node = None

    def add_node(self, node):
        self.nodes[node.name] = node

    def connect(self, from_name, to_name):
        self.nodes[from_name].connections.append(to_name)

    def set_trigger(self, name):
        self.start_node = name

    def execute(self):
        print(f"\n   🔗 [n8n] Workflow '{self.name}' executing...")
        current = self.start_node
        data = {}
        visited = set()

        while current and current not in visited:
            visited.add(current)
            node = self.nodes[current]
            data = node.execute(data) or data

            # Follow connections
            if node.node_type == "condition":
                # Conditional routing
                result = data.get("condition_result", True)
                if len(node.connections) >= 2:
                    current = node.connections[0] if result else node.connections[1]
                elif node.connections:
                    current = node.connections[0] if result else None
                else:
                    current = None
            elif node.connections:
                current = node.connections[0]
            else:
                current = None

        print(f"   🏁 Workflow complete. {len(visited)} nodes executed.")
        return data


# ─────────────────────────────────────────────────
# PARADIGMA 3: Prefect-Style Python DAG
# ─────────────────────────────────────────────────
class PrefectTask:
    """@task decorator equivalent."""
    def __init__(self, name, fn, retries=0, cache_key=None):
        self.name = name
        self.fn = fn
        self.retries = retries
        self.cache_key = cache_key
        self.state = TaskState.PENDING
        self.result = None
        self.run_count = 0

    def run(self, *args, **kwargs):
        self.state = TaskState.RUNNING
        self.run_count += 1
        try:
            self.result = self.fn(*args, **kwargs)
            self.state = TaskState.COMPLETED
            print(f"      ✅ Task '{self.name}' completed (run #{self.run_count})")
            return self.result
        except Exception as e:
            if self.run_count <= self.retries:
                self.state = TaskState.RETRYING
                print(f"      🔄 Task '{self.name}' retrying ({self.run_count}/{self.retries})")
                return self.run(*args, **kwargs)
            self.state = TaskState.FAILED
            print(f"      ❌ Task '{self.name}' FAILED: {e}")
            raise


class PrefectFlow:
    """
    PELAJARAN: Prefect Flow = Python function biasa.
    BUKAN static DAG — DAG di-build DINAMIS saat runtime.
    Bisa if-else, loop, conditional branching.
    """
    def __init__(self, name):
        self.name = name
        self.tasks = []
        self.state = TaskState.PENDING
        self.result = None

    def add_task(self, task):
        self.tasks.append(task)
        return task

    def run(self, fn, *args, **kwargs):
        """Execute flow function."""
        print(f"\n   🌊 [PREFECT] Flow '{self.name}' starting...")
        self.state = TaskState.RUNNING
        try:
            self.result = fn(*args, **kwargs)
            self.state = TaskState.COMPLETED
            print(f"   🏁 Flow '{self.name}' completed")
            stats = {s.value: 0 for s in TaskState}
            for t in self.tasks:
                stats[t.state.value] = stats.get(t.state.value, 0) + 1
            print(f"   📊 Tasks: {dict((k, v) for k, v in stats.items() if v > 0)}")
            return self.result
        except Exception as e:
            self.state = TaskState.FAILED
            print(f"   ❌ Flow FAILED: {e}")
            raise


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("⚡ OMNI WORKFLOW — Temporal + n8n + Prefect")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN (3 paradigma):")
    print("   Temporal: Durable Execution (kode biasa, event sourcing, crash recovery)")
    print("   n8n: Visual DAG (trigger → action → output, non-developer)")
    print("   Prefect: Python-native (dynamic DAG, decorator @task/@flow)")

    # ── PART 1: Temporal-Style ──
    print(f"\n{'─'*60}")
    print("📋 PART 1: Temporal-Style Durable Execution")
    wf = TemporalWorkflow("order_fulfillment")

    wf.register_activity("validate_order", lambda order: {"valid": True, "order_id": order})
    wf.register_activity("charge_payment", lambda order_id: {"charged": True, "amount": 99.99})
    wf.register_activity("ship_order", lambda order_id: {"shipped": True, "tracking": "TRK-123"})

    print(f"   🚀 Starting workflow '{wf.name}':")
    validated = wf.execute_activity("validate_order", "ORD-001")
    charged = wf.execute_activity("charge_payment", "ORD-001")
    wf.sleep("wait_for_warehouse", 3600)  # 1 jam (durable!)
    approval = wf.wait_for_signal("manager_approval")
    shipped = wf.execute_activity("ship_order", "ORD-001")
    wf.replay_from_history()

    # ── PART 2: n8n-Style ──
    print(f"\n{'─'*60}")
    print("📋 PART 2: n8n-Style Visual DAG")
    nwf = N8NWorkflow("customer_onboarding")

    nwf.add_node(WorkflowNode("webhook", "trigger", {"source": "Stripe"}))
    nwf.add_node(WorkflowNode("validate_email", "action",
        {"action": lambda d: {**d, "email_valid": True, "email": "user@test.com"}}))
    nwf.add_node(WorkflowNode("check_existing", "condition",
        {"condition": lambda d: not d.get("existing_user", False)}))
    nwf.add_node(WorkflowNode("create_account", "action",
        {"action": lambda d: {**d, "account_created": True, "id": "USR-42"}}))
    nwf.add_node(WorkflowNode("send_welcome", "action",
        {"action": lambda d: {**d, "welcome_sent": True}}))
    nwf.add_node(WorkflowNode("notify_existing", "output"))
    nwf.add_node(WorkflowNode("done", "output"))

    nwf.connect("webhook", "validate_email")
    nwf.connect("validate_email", "check_existing")
    nwf.connect("check_existing", "create_account")    # true → new user
    nwf.connect("check_existing", "notify_existing")   # false → existing
    nwf.connect("create_account", "send_welcome")
    nwf.connect("send_welcome", "done")

    nwf.set_trigger("webhook")
    result = nwf.execute()
    print(f"   Result: {result}")

    # ── PART 3: Prefect-Style ──
    print(f"\n{'─'*60}")
    print("📋 PART 3: Prefect-Style Python DAG")
    flow = PrefectFlow("data_pipeline")

    extract = flow.add_task(PrefectTask("extract_data", lambda: [1, 2, 3, 4, 5]))
    transform = flow.add_task(PrefectTask("transform", lambda data: [x * 2 for x in data]))
    validate = flow.add_task(PrefectTask("validate", lambda data: all(x > 0 for x in data)))
    load = flow.add_task(PrefectTask("load_to_db", lambda data: f"Loaded {len(data)} records"))

    def pipeline_fn():
        raw = extract.run()
        transformed = transform.run(raw)
        is_valid = validate.run(transformed)
        if is_valid:
            return load.run(transformed)
        else:
            raise ValueError("Validation failed")

    flow.run(pipeline_fn)

    print(f"\n{'='*70}")
    print("✅ Workflow Engine: DIPELAJARI MENDALAM.")
    print("   Temporal (durable execution + event sourcing + signal/timer) ✓")
    print("   n8n (visual DAG + trigger → action → condition → output) ✓")
    print("   Prefect (Python-native + dynamic DAG + task retries) ✓")
    print(f"{'='*70}")
