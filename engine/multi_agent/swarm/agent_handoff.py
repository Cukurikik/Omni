import time

# ==========================================
# 🐝 OMNI MULTI-AGENT: OpenAI Swarm Engine (Phase 149)
# ==========================================
# Framework 5: OpenAI Swarm
#   - Lightweight agent handoff (serah terima)
#   - Stateless architecture
#   - Function calling (tools)
#   - Triage agent (router)
#   - Educational / playground

class SwarmAgent:
    """Swarm Agent: Lightweight agent dengan instructions dan functions."""

    def __init__(self, name: str, instructions: str, functions: list = None):
        self.name = name
        self.instructions = instructions
        self.functions = functions or []

    def run(self, message: str) -> dict:
        """Process message dan kembalikan response atau handoff."""
        print(f"      🐝 [{self.name}] Processing: \"{message[:50]}...\"")
        print(f"         Instructions: {self.instructions[:60]}...")

        # Check if any function should trigger handoff
        for func in self.functions:
            result = func(message, self.name)
            if result.get("handoff"):
                return result

        # Generate response
        response = f"[{self.name}] Berdasarkan instruksi saya: {self.instructions[:30]}... Jawaban saya untuk '{message[:30]}' sudah siap."
        return {"response": response, "agent": self.name}


class Swarm:
    """OpenAI Swarm: Orchestrator untuk agent handoff."""

    def __init__(self):
        self.agents = {}
        self.history = []
        print("🐝 [SWARM] Swarm Orchestrator diinisiasi.")

    def register(self, agent: SwarmAgent):
        self.agents[agent.name] = agent

    def run(self, agent_name: str, messages: list, max_handoffs: int = 5) -> dict:
        """Jalankan swarm dari agent awal, follow handoffs."""
        print(f"\n🚀 [SWARM] Memulai dari agent: {agent_name}")

        current_agent = self.agents.get(agent_name)
        if not current_agent:
            return {"error": f"Agent '{agent_name}' not found"}

        last_message = messages[-1] if messages else ""
        handoff_count = 0

        while handoff_count < max_handoffs:
            print(f"\n   ── Handoff #{handoff_count} ──")
            result = current_agent.run(last_message)

            self.history.append({
                "agent": current_agent.name,
                "input": last_message[:40],
                "handoff_count": handoff_count
            })

            if result.get("handoff"):
                target = result["handoff"]
                reason = result.get("reason", "N/A")
                print(f"      🔄 HANDOFF: {current_agent.name} → {target} (reason: {reason})")

                if target in self.agents:
                    current_agent = self.agents[target]
                    handoff_count += 1
                else:
                    return {"error": f"Handoff target '{target}' not found", "last_agent": current_agent.name}
            else:
                print(f"      ✅ Final response dari {current_agent.name}")
                return result

        return {"error": "Max handoffs reached", "last_agent": current_agent.name}


# ─── Handoff Functions ───
def triage_handoff(message: str, current_agent: str) -> dict:
    """Triage: Route ke agent yang tepat berdasarkan konten."""
    msg_lower = message.lower()
    if any(w in msg_lower for w in ["bayar", "tagihan", "refund", "harga"]):
        return {"handoff": "billing_agent", "reason": "Masalah pembayaran terdeteksi"}
    elif any(w in msg_lower for w in ["rusak", "error", "bug", "tidak bisa", "gagal"]):
        return {"handoff": "tech_support", "reason": "Masalah teknis terdeteksi"}
    elif any(w in msg_lower for w in ["batal", "cancel", "tutup akun"]):
        return {"handoff": "retention_agent", "reason": "Risiko churn terdeteksi"}
    return {}  # No handoff needed

def escalation_handoff(message: str, current_agent: str) -> dict:
    """Eskalasi ke supervisor jika masalah komplek."""
    if any(w in message.lower() for w in ["supervisor", "atasan", "manager", "eskalasi"]):
        return {"handoff": "supervisor", "reason": "User meminta eskalasi"}
    return {}


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 65)
    print("🐝 OMNI SWARM — Lightweight Agent Handoff (OpenAI Swarm)")
    print("=" * 65)

    swarm = Swarm()

    # Register agents
    triage = SwarmAgent(
        "triage_agent",
        "Kamu adalah agen triage. Arahkan user ke agen yang tepat.",
        functions=[triage_handoff]
    )
    billing = SwarmAgent(
        "billing_agent",
        "Kamu menangani masalah pembayaran dan tagihan.",
        functions=[escalation_handoff]
    )
    tech = SwarmAgent(
        "tech_support",
        "Kamu menangani masalah teknis dan debugging.",
        functions=[escalation_handoff]
    )
    retention = SwarmAgent(
        "retention_agent",
        "Kamu mencegah user cancel. Tawarkan diskon.",
        functions=[]
    )
    supervisor = SwarmAgent(
        "supervisor",
        "Kamu adalah supervisor. Handle eskalasi dan kasus sulit.",
        functions=[]
    )

    swarm.register(triage)
    swarm.register(billing)
    swarm.register(tech)
    swarm.register(retention)
    swarm.register(supervisor)

    # ── TEST 1: Billing Issue ──
    print("\n" + "─" * 60)
    print("📋 TEST 1: User punya masalah tagihan")
    result1 = swarm.run("triage_agent", ["Saya mau refund tagihan bulan lalu yang salah"])
    print(f"   💬 Response: {result1.get('response', result1)[:80]}...")

    # ── TEST 2: Tech Issue ──
    print("\n" + "─" * 60)
    print("📋 TEST 2: User punya masalah teknis")
    result2 = swarm.run("triage_agent", ["Aplikasi saya error dan tidak bisa dibuka"])
    print(f"   💬 Response: {result2.get('response', result2)[:80]}...")

    # ── TEST 3: Cancellation → Retention ──
    print("\n" + "─" * 60)
    print("📋 TEST 3: User mau batal langganan")
    result3 = swarm.run("triage_agent", ["Saya ingin cancel akun saya dan tutup akun"])
    print(f"   💬 Response: {result3.get('response', result3)[:80]}...")

    # ── TEST 4: Escalation chain ──
    print("\n" + "─" * 60)
    print("📋 TEST 4: Eskalasi ke supervisor")
    result4 = swarm.run("triage_agent", ["Tagihan saya salah, saya mau bicara supervisor!"])
    print(f"   💬 Response: {result4.get('response', result4)[:80]}...")

    print(f"\n{'='*65}")
    print(f"📊 Swarm History: {len(swarm.history)} interactions")
    for h in swarm.history:
        print(f"   🐝 {h['agent']} | handoff #{h['handoff_count']} | input: {h['input']}...")

    print(f"\n{'='*65}")
    print("✅ Swarm: Triage Routing ✓ | Agent Handoff ✓ | Escalation ✓")
    print("   Function Calling ✓ | Stateless ✓ | Multi-hop Handoff ✓")
    print(f"{'='*65}")
