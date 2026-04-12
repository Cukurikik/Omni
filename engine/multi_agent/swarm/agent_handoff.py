import time

# ==========================================
# 🐝 OMNI MULTI-AGENT: OpenAI Swarm — REWRITE MENDALAM (Phase 154)
# ==========================================
#
# PROSES BELAJAR JUJUR:
# ──────────────────────
# Versi sebelumnya SALAH. Saya TIDAK implementasi context_variables
# sama sekali, padahal ini adalah SEPARUH dari inti arsitektur Swarm.
#
# Setelah membaca source code dan dokumentasi, saya menemukan:
#
# 1. CONTEXT VARIABLES — shared dict yang persisten selama eksekusi.
#    Ketika agent di-handoff, context_variables IKUT berpindah.
#    Ini berarti agent baru punya AKSES ke semua data yang
#    dikumpulkan agent sebelumnya.
#    Tools bisa MEMBACA dan MENGUPDATE context_variables.
#
# 2. THE WHILE LOOP — Swarm bukan tree/graph.
#    Internal Swarm adalah while loop sederhana:
#    while True:
#      response = get_completion(active_agent)
#      if tool_call:
#        result = execute_tool(tool_call)
#        if result is Agent:
#          active_agent = result  # HANDOFF!
#      else:
#        break  # final response
#
# 3. HANDOFF = TOOL YANG RETURN AGENT.
#    Handoff bukan "event" khusus. Ini hanyalah tool function
#    biasa yang MENGEMBALIKAN Agent object. Swarm mendeteksi
#    bahwa return value adalah Agent, dan MENGGANTI active_agent.
#
# 4. STATELESS BETWEEN RUNS.
#    Swarm TIDAK menyimpan state antar client.run() calls.
#    Semua "memori" ada di messages list dan context_variables.

class Agent:
    """Swarm Agent: instructions + functions + context dependency."""
    def __init__(self, name, instructions, functions=None):
        self.name = name
        self.instructions = instructions
        self.functions = functions or []

    def __repr__(self):
        return f"Agent({self.name})"


class Response:
    """Swarm Response object."""
    def __init__(self, messages, agent, context_variables):
        self.messages = messages
        self.agent = agent
        self.context_variables = context_variables


class Swarm:
    """
    OpenAI Swarm — VERSI YANG BENAR.
    Implementasi while-loop internal + context_variables + handoff detection.
    """

    def __init__(self):
        print("🐝 [SWARM] Client diinisiasi (stateless between runs).")

    def run(self, agent, messages, context_variables=None, max_turns=10):
        """
        THE CORE LOOP — ini yang terjadi di dalam Swarm:
        1. Get completion dari active_agent
        2. Jika ada tool call, eksekusi tool
        3. Jika tool return Agent object → HANDOFF
        4. Jika tool return string → append ke messages
        5. Jika tidak ada tool call → selesai
        """
        active_agent = agent
        ctx = context_variables or {}
        all_messages = list(messages)
        turn = 0

        print(f"\n🚀 [SWARM.RUN] Starting agent: {active_agent.name}")
        print(f"   Context: {ctx}")
        print(f"   Messages: {len(all_messages)} initial\n")

        while turn < max_turns:
            turn += 1
            print(f"   ── Turn {turn} (active: {active_agent.name}) ──")

            # Step 1: "Get completion" — simulasi LLM deciding what to do
            user_msg = all_messages[-1] if all_messages else ""
            user_content = user_msg.get("content", "") if isinstance(user_msg, dict) else str(user_msg)

            # Step 2: Check if any function should be called
            tool_called = False
            for func in active_agent.functions:
                # PELAJARAN: Tool menerima context_variables sebagai parameter
                result = func(user_content, ctx)

                if result is None:
                    continue

                tool_called = True

                # Step 3: HANDOFF DETECTION — jika result adalah Agent, GANTI active_agent
                if isinstance(result, Agent):
                    print(f"      🔄 [HANDOFF] {active_agent.name} → {result.name}")
                    print(f"         Context carried: {list(ctx.keys())}")
                    active_agent = result
                    all_messages.append({"role": "system", "content": f"Transferred to {result.name}"})
                    break

                elif isinstance(result, dict):
                    # Tool bisa update context_variables
                    if "context_update" in result:
                        ctx.update(result["context_update"])
                        print(f"      📝 Context updated: {list(result['context_update'].keys())}")
                    if "response" in result:
                        all_messages.append({"role": active_agent.name, "content": result["response"]})
                        print(f"      💬 {active_agent.name}: {result['response'][:60]}...")
                    if result.get("done"):
                        print(f"      ✅ Agent {active_agent.name} selesai.")
                        return Response(all_messages, active_agent, ctx)
                    break

                elif isinstance(result, str):
                    all_messages.append({"role": active_agent.name, "content": result})
                    print(f"      💬 {active_agent.name}: {result[:60]}...")
                    break

            if not tool_called:
                # Tidak ada tool yang cocok — agent memberikan respons final
                response = f"[{active_agent.name}] {active_agent.instructions[:40]}... Saya membantu Anda."
                all_messages.append({"role": active_agent.name, "content": response})
                print(f"      💬 {active_agent.name} (final): {response[:60]}...")
                return Response(all_messages, active_agent, ctx)

        return Response(all_messages, active_agent, ctx)


# ─── Agent Functions (with context_variables) ───

def triage_fn(user_msg, ctx):
    """Triage: Route berdasarkan content + update context."""
    msg = user_msg.lower()
    if any(w in msg for w in ["bayar", "tagihan", "refund", "harga"]):
        ctx["issue_type"] = "billing"
        ctx["priority"] = "high" if "refund" in msg else "medium"
        return billing_agent  # RETURN AGENT = HANDOFF!
    elif any(w in msg for w in ["rusak", "error", "bug", "tidak bisa"]):
        ctx["issue_type"] = "technical"
        ctx["priority"] = "high"
        return tech_agent
    elif any(w in msg for w in ["batal", "cancel", "tutup"]):
        ctx["issue_type"] = "retention"
        ctx["priority"] = "critical"
        return retention_agent
    return None  # Tidak ada routing

def billing_fn(user_msg, ctx):
    """Billing agent: Gunakan context_variables."""
    issue = ctx.get("issue_type", "unknown")
    priority = ctx.get("priority", "low")
    if any(w in user_msg.lower() for w in ["supervisor", "manager", "atasan"]):
        ctx["escalation_reason"] = "customer_requested"
        return supervisor_agent  # ESCALATION HANDOFF
    return {
        "response": f"[Billing] Saya menangani masalah {issue} Anda (prioritas: {priority}). Refund sedang diproses.",
        "context_update": {"billing_status": "processing_refund"},
        "done": True
    }

def tech_fn(user_msg, ctx):
    issue = ctx.get("issue_type", "unknown")
    return {
        "response": f"[Tech] Mengecek masalah {issue}. Error telah diidentifikasi dan diperbaiki.",
        "context_update": {"tech_status": "resolved", "fix_applied": True},
        "done": True
    }

def retention_fn(user_msg, ctx):
    return {
        "response": f"[Retention] Kami tidak ingin kehilangan Anda! Berikut diskon 40% untuk 3 bulan.",
        "context_update": {"offer_sent": "40% discount", "retention_status": "offer_extended"},
        "done": True
    }

def supervisor_fn(user_msg, ctx):
    escalation = ctx.get("escalation_reason", "N/A")
    billing_status = ctx.get("billing_status", "N/A")
    return {
        "response": f"[Supervisor] Saya melihat eskalasi ({escalation}), billing: {billing_status}. Masalah Anda sudah saya prioritaskan.",
        "context_update": {"resolved_by": "supervisor", "final_status": "resolved"},
        "done": True
    }

# Definisikan agents
triage_agent = Agent("Triage", "Saya router pertama. Saya menganalisis masalah dan mengarahkan ke spesialis.", [triage_fn])
billing_agent = Agent("Billing", "Saya menangani pembayaran, tagihan, dan refund.", [billing_fn])
tech_agent = Agent("TechSupport", "Saya menangani masalah teknis, bug, dan error.", [tech_fn])
retention_agent = Agent("Retention", "Saya mencegah churn. Saya menawarkan diskon.", [retention_fn])
supervisor_agent = Agent("Supervisor", "Saya menangani eskalasi dan kasus sulit.", [supervisor_fn])


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("🐝 OMNI SWARM v2 — REWRITE MENDALAM (Context Variables + While Loop)")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN:")
    print("   Versi lama: TIDAK ada context_variables. Handoff 'kosong'.")
    print("   SALAH karena: Context variables adalah SEPARUH inti Swarm.")
    print("   Ketika handoff, context_variables IKUT berpindah ke agent baru.")
    print("   Agent baru TAHU apa yang sudah dikerjakan agent sebelumnya.")
    print("   Internal Swarm = while loop: completion → tool → handoff check → repeat")
    print()

    client = Swarm()

    # TEST 1: Billing → langsung resolved
    print("─" * 60)
    print("📋 TEST 1: Billing Issue (context propagation)")
    r1 = client.run(triage_agent,
                    [{"role": "user", "content": "Saya mau refund tagihan bulan lalu yang salah"}],
                    context_variables={"customer_id": "C123", "account_type": "premium"})
    print(f"   📊 Final context: {r1.context_variables}")

    # TEST 2: Tech issue
    print("\n" + "─" * 60)
    print("📋 TEST 2: Tech Issue (context propagation)")
    r2 = client.run(triage_agent,
                    [{"role": "user", "content": "Aplikasi saya error tidak bisa dibuka"}],
                    context_variables={"customer_id": "C456"})
    print(f"   📊 Final context: {r2.context_variables}")

    # TEST 3: Retention
    print("\n" + "─" * 60)
    print("📋 TEST 3: Retention (anti-churn)")
    r3 = client.run(triage_agent,
                    [{"role": "user", "content": "Saya mau cancel langganan"}],
                    context_variables={"customer_id": "C789", "months_subscribed": 14})
    print(f"   📊 Final context: {r3.context_variables}")

    # TEST 4: Multi-hop escalation
    print("\n" + "─" * 60)
    print("📋 TEST 4: Multi-hop Escalation (triage→billing→supervisor)")
    r4 = client.run(triage_agent,
                    [{"role": "user", "content": "Tagihan salah! Saya mau bicara supervisor!"}],
                    context_variables={"customer_id": "C999", "vip": True})
    print(f"   📊 Final context: {r4.context_variables}")

    print(f"\n{'='*70}")
    print("✅ Swarm v2: BENAR dipelajari ulang.")
    print("   context_variables (shared dict + propagation) ✓")
    print("   While loop internal (completion → tool → handoff check) ✓")
    print("   Handoff = tool return Agent object ✓")
    print("   Stateless between runs ✓")
    print("   Context updates by tools ✓")
    print(f"{'='*70}")
