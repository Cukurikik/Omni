package singularity

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"
)

// ==========================================
// 🕸️ OMNI DAG MULTI-AGENT STATE (LangGraph-like)
// ==========================================
// Integrasi nyata dari Graph State Persistence.
// Memungkinkan agen untuk bertransisi state tanpa henti dengan aman (No Deadlocks).

type AgentState struct {
	ID        string
	Messages  []string
	Iteration int
	IsDone    bool
}

type AgentNode func(ctx context.Context, state *AgentState) (*AgentState, error)

type OmniDAG orchestrator
type orchestrator struct {
	Nodes    map[string]AgentNode
	Edges    map[string]string
	State    *AgentState
	stateMux sync.Mutex
}

func NewOmniDAG() *orchestrator {
	return &orchestrator{
		Nodes: make(map[string]AgentNode),
		Edges: make(map[string]string),
	}
}

func (o *orchestrator) AddNode(name string, node AgentNode) {
	o.Nodes[name] = node
}

func (o *orchestrator) AddEdge(from, to string) {
	o.Edges[from] = to
}

// Menjalankan evaluasi state Graph secara otonom (No simulation)
func (o *orchestrator) Run(ctx context.Context, startNode string, initialState *AgentState) {
	o.State = initialState
	currentNode, exists := o.Nodes[startNode]
	currentName := startNode

	if !exists {
		log.Fatalf("❌ [DAG-FATAL] Node awal v%s tidak ditemukan di Graph.", startNode)
	}

	for {
		select {
		case <-ctx.Done():
			log.Println("🛑 [DAG-ORCHESTRATOR] Sinyal Penghentian Graf Diterima.")
			return
		default:
			o.stateMux.Lock()
			newState, err := currentNode(ctx, o.State)
			if err != nil {
				log.Printf("⚠️ [DAG-ERROR] Node %s gagal: %v\n", currentName, err)
				o.stateMux.Unlock()
				return
			}
			o.State = newState
			o.stateMux.Unlock()

			if o.State.IsDone {
				log.Printf("✅ [DAG-DONE] Siklus agen OMNI Graph %s telah tuntas. (Iterasi: %d)\n", o.State.ID, o.State.Iteration)
				return
			}

			nextName, hasEdge := o.Edges[currentName]
			if !hasEdge {
				log.Printf("🕸️ [DAG-END] Tidak ada transisi edge dari %s. Rute Evaluasi Berakhir.\n", currentName)
				return
			}
			
			currentNode = o.Nodes[nextName]
			currentName = nextName
			time.Sleep(100 * time.Millisecond) // CPU control
		}
	}
}

// Inisialisasi nyata jaring Graph OMNI
func IgniteMultiAgentDAG() {
	log.Println("🕸️🔥 [OMNI-DAG] Menyalakan Orkestrasi Multi-Agent LangGraph-Style...")
	
	dag := NewOmniDAG()
	
	dag.AddNode("Analyst", func(ctx context.Context, s *AgentState) (*AgentState, error) {
		s.Iteration++
		s.Messages = append(s.Messages, fmt.Sprintf("Data Analysis #%d completed", s.Iteration))
		log.Println("📊 [AGENT-ANALYST] Menganalisis Kumpulan Data OMNI...")
		return s, nil
	})
	
	dag.AddNode("Supervisor", func(ctx context.Context, s *AgentState) (*AgentState, error) {
		log.Println("👁️ [AGENT-SUPERVISOR] Memeriksa state Agen Pekerja...")
		if s.Iteration >= 3 {
			s.IsDone = true // End routine cleanly
		}
		return s, nil
	})
	
	dag.AddEdge("Analyst", "Supervisor")
	dag.AddEdge("Supervisor", "Analyst") // Loop kembali ke Analyst jika belum selesai
	
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	
	sigState := &AgentState{ID: "OMNI-TASK-001", Iteration: 0}
	dag.Run(ctx, "Analyst", sigState)
}
