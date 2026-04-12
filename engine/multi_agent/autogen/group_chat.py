import time

# ==========================================
# 💬 OMNI MULTI-AGENT: AutoGen — REWRITE MENDALAM (Phase 152)
# ==========================================
#
# PROSES BELAJAR JUJUR:
# ──────────────────────
# Versi sebelumnya SALAH. GroupChat saya hanya round-robin bodoh
# dimana agent bergantian ngomong tanpa logika.
#
# Setelah riset mendalam, saya menemukan:
#
# 1. GROUP CHAT MANAGER (GCM) ADALAH AGENT TERSENDIRI.
#    GCM BUKAN hanya "scheduler". GCM adalah agent dengan LLM
#    sendiri yang MENGANALISIS percakapan dan MEMUTUSKAN siapa
#    yang harus bicara selanjutnya berdasarkan KONTEKS.
#
# 2. SPEAKER SELECTION MODES:
#    - auto: GCM menggunakan LLM untuk memilih speaker terbaik
#    - round_robin: giliran berputar
#    - random: acak
#    - manual: user memilih (HITL)
#    - custom function: developer menentukan state machine
#
# 3. ALLOWED TRANSITIONS (State Machine):
#    Developer bisa membatasi siapa boleh bicara setelah siapa.
#    Ini MENCEGAH alur yang tidak logis (misal: QA bicara
#    sebelum Developer menulis kode).
#
# 4. DESCRIPTION ATTRIBUTE:
#    `description` field di setiap agent SANGAT PENTING untuk
#    mode "auto" — GCM membaca description untuk memutuskan
#    siapa yang paling relevan untuk merespons.

class ConversableAgent:
    def __init__(self, name, system_message="", description="",
                 human_input_mode="NEVER"):
        self.name = name
        self.system_message = system_message
        self.description = description  # PELAJARAN: ini yang dibaca GCM
        self.human_input_mode = human_input_mode
        self.chat_history = []

    def generate_reply(self, messages, sender_name=""):
        """Simulasi LLM reasoning berdasarkan system_message dan konteks."""
        last_msg = messages[-1]["content"] if messages else ""
        last_speaker = messages[-1]["role"] if messages else ""

        # Agent merespons berdasarkan system_message dan konteks
        if "plan" in self.system_message.lower():
            reply = f"Rencana saya: (1) Definisikan scope, (2) Pilih arsitektur, (3) Implementasi bertahap. Berdasarkan '{last_msg[:30]}...'"
        elif "code" in self.system_message.lower() or "engineer" in self.system_message.lower():
            reply = f"```python\ndef solve():\n    # Implementasi berdasarkan rencana\n    return 'solution'\n```\nKode sudah ditulis berdasarkan rencana {last_speaker}."
        elif "review" in self.system_message.lower() or "critic" in self.system_message.lower():
            reply = f"Review: (1) Kode perlu error handling, (2) Tambahkan docstring, (3) Testing 85% coverage. Secara keseluruhan bagus."
        elif "test" in self.system_message.lower() or "qa" in self.system_message.lower():
            reply = f"Test results: 12/12 passed. Coverage: 87%. Tidak ada bug kritis ditemukan."
        elif "user" in self.name.lower() or "proxy" in self.name.lower():
            reply = f"Terima kasih tim, hasilnya memuaskan. TERMINATE"
        else:
            reply = f"Saya {self.name}: Melengkapi perspektif dari {last_speaker} tentang {last_msg[:25]}..."

        self.chat_history.append({"role": self.name, "content": reply})
        return reply


class GroupChatManager:
    """
    PELAJARAN KUNCI: GroupChatManager adalah AGENT TERSENDIRI.
    GCM punya LLM sendiri yang membaca:
    1. Deskripsi semua agent
    2. History percakapan
    3. Allowed transitions (jika ada)
    Lalu MEMUTUSKAN siapa yang bicara berikutnya.
    """

    def __init__(self, agents, max_round=10, speaker_selection="auto",
                 allowed_transitions=None):
        self.agents = agents
        self.max_round = max_round
        self.speaker_selection = speaker_selection
        self.allowed_transitions = allowed_transitions  # {agent: [allowed_next_agents]}
        self.messages = []

        print(f"💬 [AUTOGEN] GroupChatManager diinisiasi:")
        print(f"   Selection: {speaker_selection} | Max rounds: {max_round}")
        print(f"   Agents:")
        for a in agents:
            print(f"      🗣️ {a.name}: {a.description[:50]}...")
        if allowed_transitions:
            print(f"   🔒 Allowed transitions defined ({len(allowed_transitions)} rules)")

    def _select_speaker_auto(self, last_speaker, round_num):
        """
        PELAJARAN: Mode 'auto' menggunakan LLM untuk memilih.
        GCM membaca DESCRIPTION setiap agent dan HISTORY percakapan,
        lalu memutuskan siapa yang paling relevan.
        """
        candidates = [a for a in self.agents if a != last_speaker]

        # Filter berdasarkan allowed_transitions (jika ada)
        if self.allowed_transitions and last_speaker:
            allowed = self.allowed_transitions.get(last_speaker.name, [])
            if allowed:
                candidates = [a for a in candidates if a.name in allowed]
                print(f"      🔒 Transition filter: {last_speaker.name} → {[a.name for a in candidates]}")

        if not candidates:
            return self.agents[0]

        # Simulasi LLM reasoning: pilih berdasarkan relevansi description
        last_content = self.messages[-1]["content"] if self.messages else ""
        best_agent = candidates[0]
        best_score = 0
        for agent in candidates:
            # Hitung relevansi description agent dengan pesan terakhir
            desc_words = set(agent.description.lower().split())
            msg_words = set(last_content.lower().split())
            score = len(desc_words & msg_words)
            if score > best_score:
                best_score = score
                best_agent = agent

        print(f"      🧠 [GCM] Auto-selected: {best_agent.name} (relevance score: {best_score})")
        return best_agent

    def _select_speaker(self, last_speaker, round_num):
        if self.speaker_selection == "round_robin":
            idx = round_num % len(self.agents)
            return self.agents[idx]
        elif self.speaker_selection == "random":
            import random
            return random.choice(self.agents)
        elif self.speaker_selection == "auto":
            return self._select_speaker_auto(last_speaker, round_num)
        return self.agents[0]

    def run(self, initial_message):
        print(f"\n🚀 [GROUP CHAT] Topik: \"{initial_message[:60]}...\"\n")
        self.messages.append({"role": "system", "content": initial_message})

        last_speaker = None
        for round_num in range(self.max_round):
            speaker = self._select_speaker(last_speaker, round_num)

            print(f"   ── Round {round_num+1}/{self.max_round} ──")
            reply = speaker.generate_reply(self.messages, last_speaker.name if last_speaker else "system")
            self.messages.append({"role": speaker.name, "content": reply})
            print(f"   🗣️ [{speaker.name}]: {reply[:70]}...")

            last_speaker = speaker

            if "TERMINATE" in reply.upper():
                print(f"\n   🛑 Percakapan diakhiri oleh {speaker.name} (round {round_num+1})")
                break

        return self.messages


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("💬 OMNI AUTOGEN v2 — REWRITE MENDALAM (GCM + Auto Selection + Transitions)")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN:")
    print("   Versi lama: Round-robin bodoh tanpa logika.")
    print("   SALAH karena: GroupChatManager seharusnya AGENT TERSENDIRI")
    print("   yang menggunakan LLM untuk MEMUTUSKAN siapa bicara next.")
    print("   Mode 'auto' membaca DESCRIPTION setiap agent.")
    print("   Allowed transitions membatasi alur percakapan.")
    print()

    planner = ConversableAgent("Planner",
        "Kamu membuat rencana detail untuk proyek software.",
        "Expert di project planning, arsitektur, dan task decomposition")
    coder = ConversableAgent("Coder",
        "Kamu menulis kode Python berkualitas tinggi.",
        "Expert kode Python, implementasi, algorithm, dan data structure")
    reviewer = ConversableAgent("Reviewer",
        "Kamu mereview kode dan memberikan feedback kritis.",
        "Expert code review, testing, quality assurance, dan best practices")
    tester = ConversableAgent("Tester",
        "Kamu menulis dan menjalankan test suite.",
        "Expert testing, QA, unit test, integration test, dan coverage")
    user = ConversableAgent("UserProxy",
        "Kamu mewakili user dan memberikan approval final.",
        "User representative yang mengecek apakah hasil memuaskan")

    # TEST 1: Auto selection DENGAN allowed transitions
    print("─" * 60)
    print("📋 TEST 1: Auto Selection + Allowed Transitions")
    gcm1 = GroupChatManager(
        [planner, coder, reviewer, tester, user],
        max_round=8,
        speaker_selection="auto",
        allowed_transitions={
            "Planner": ["Coder"],             # Planner → hanya Coder
            "Coder": ["Reviewer"],            # Coder → hanya Reviewer
            "Reviewer": ["Coder", "Tester"],  # Reviewer → Coder (revisi) / Tester
            "Tester": ["UserProxy"],           # Tester → UserProxy
            "UserProxy": [],                   # User → end
        }
    )
    gcm1.run("Bangun REST API untuk multi-agent task management system")

    # TEST 2: Round robin tanpa restrictions
    print("\n" + "─" * 60)
    print("📋 TEST 2: Round Robin (tanpa filter)")
    gcm2 = GroupChatManager(
        [planner, coder, reviewer],
        max_round=4,
        speaker_selection="round_robin"
    )
    gcm2.run("Diskusikan arsitektur terbaik untuk MAS")

    print(f"\n{'='*70}")
    print("✅ AutoGen v2: BENAR dipelajari ulang.")
    print("   GroupChatManager sebagai agent tersendiri ✓")
    print("   Auto selection berdasarkan description + relevance scoring ✓")
    print("   Allowed transitions (state machine) ✓")
    print("   Termination condition ✓")
    print(f"{'='*70}")
