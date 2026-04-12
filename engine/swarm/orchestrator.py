import time
from collections import deque

# ==========================================
# 🧠 OMNI SWARM V2: LangGraph & CrewAI Convergence
# ==========================================
# Implementasi State Graph untuk Multiple Agents dengan memory-sharing
# dan tools delegation.

class SwarmState:
    def __init__(self):
        self.memory = {}
        self.message_history = []
        self.current_node = "START"

class OMNIAgent:
    def __init__(self, name, instruction):
        self.name = name
        self.instruction = instruction

    def invoke(self, state: SwarmState):
        print(f"🤖 [{self.name}] Analyzing state... ({self.instruction})")
        time.sleep(0.5)
        response = f"Result from {self.name}: Task solved based on past memory."
        state.message_history.append(response)
        return state

class OmniGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        
    def add_node(self, name, function):
        self.nodes[name] = function
        
    def add_edge(self, from_node, to_node):
        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append(to_node)

    def compile_and_run(self, initial_state: SwarmState):
        print("🕸️ Menyusun Peta Eksekusi (Graph Orchestration)...")
        queue = deque(["START"])
        
        while queue:
            current = queue.popleft()
            if current == "END":
                break
            
            if current in self.nodes:
                initial_state = self.nodes[current](initial_state)
            
            if current in self.edges:
                for nxt in self.edges[current]:
                    queue.append(nxt)
                    
        return initial_state

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 1. Definisi Agen (CrewAI Style Role-Playing)
    researcher = OMNIAgent("Researcher", "Cari informasi komprehensif di Web.")
    writer = OMNIAgent("Writer", "Susun hasil riset menjadi Laporan Enterprise.")
    
    # 2. Susun Cyclic Graph (LangGraph Style Orchestration)
    workflow = OmniGraph()
    workflow.add_node("START", lambda state: state)
    workflow.add_node("ResearchNode", researcher.invoke)
    workflow.add_node("WriterNode", writer.invoke)
    
    workflow.add_edge("START", "ResearchNode")
    workflow.add_edge("ResearchNode", "WriterNode")
    workflow.add_edge("WriterNode", "END")
    
    # 3. Eksekusi
    state = SwarmState()
    final_state = workflow.compile_and_run(state)
    
    print("✅ [SWARM V2] Laporan telah diselesaikan oleh OMNI Agent secara Kolaboratif.")
    for msg in final_state.message_history:
        print("  ->", msg)
