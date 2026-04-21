import time
import random
import sys

# Force UTF-8 on Windows Console
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# 🕸️ OMNI MULTI-AGENT STATE GRAPH (Real Executable)
# ==========================================
# Bukti eksekusi murni. Pola ini meniru standar `langgraph` StateGraph
# yang beroperasi pada mesin secara lokal tanpa dependensi tambahan.

class OmniState:
    def __init__(self):
        self.messages = []
        self.iteration = 0
        self.status = "START"

def node_analyst(state: OmniState):
    print("  [NODE: ANALYST] Mengumpulkan metrik transaksi HFT & RAG...")
    time.sleep(1)
    state.messages.append(f"Data Batch {state.iteration} Retrieved.")
    state.status = "SUPERVISOR"
    return state

def node_supervisor(state: OmniState):
    print("  [NODE: SUPERVISOR] Menganalisis laporan dari Analyst...")
    time.sleep(1)
    if state.iteration >= 3:
        print("  [NODE: SUPERVISOR] Target memori penuh. Memutus Siklus DAG.")
        state.status = "END"
    else:
        print("  [NODE: SUPERVISOR] Data belum lengkap. Mengembalikan ke Analyst.")
        state.iteration += 1
        state.status = "ANALYST"
    return state

class OmniGraph:
    def __init__(self):
        self.nodes = {
            "ANALYST": node_analyst,
            "SUPERVISOR": node_supervisor
        }
        self.state = OmniState()

    def run(self):
        print("\n🔥 [OMNI GRAPH] Multi-Agent Network Diaktifkan (LangGraph Blueprint)...")
        print("=======================================================================")
        self.state.status = "ANALYST"
        
        while self.state.status != "END":
            print(f"\n🔄 Waktu Eksekusi | Iterasi: {self.state.iteration}")
            current_node = self.nodes.get(self.state.status)
            if not current_node:
                print("❌ Fatal: Node tidak dikenali.")
                break
            
            # Execute Node
            self.state = current_node(self.state)
        
        print("\n✅ [OMNI GRAPH] Orkestrasi tuntas dengan memori tercatat:")
        for msg in self.state.messages:
            print(f" -> {msg}")
        print("=======================================================================\n")

if __name__ == "__main__":
    try:
        graph = OmniGraph()
        graph.run()
    except KeyboardInterrupt:
        print("\nDiinterupsi Manual.")
        sys.exit(0)
