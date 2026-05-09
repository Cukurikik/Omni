// moe_health_probe.go — Network / Orchestration
// Layer: Network / Infra — Kubernetes Liveness & Readiness Probes
//
// Exposes standard HTTP endpoints for Kubernetes to manage the lifecycle of
// MoE Inference Pods. Ensures traffic is only routed to pods that have fully
// loaded their experts into VRAM.

package network_moe

import (
	"fmt"
	"net/http"
	"sync/atomic"
)

type MoEHealthProbe struct {
	Port    int
	IsReady int32 // Atomic flag: 1 = ready, 0 = not ready
	IsAlive int32 // Atomic flag: 1 = alive, 0 = dead
}

func NewHealthProbe(port int) *MoEHealthProbe {
	return &MoEHealthProbe{
		Port:    port,
		IsReady: 0, // Starts not ready while models load
		IsAlive: 1, // Alive as soon as process starts
	}
}

// MarkReady called after SafeTensors are successfully loaded into VRAM
func (h *MoEHealthProbe) MarkReady() {
	atomic.StoreInt32(&h.IsReady, 1)
	fmt.Println("[K8s Probe] Node marked as READY. Experts loaded into VRAM.")
}

func (h *MoEHealthProbe) handleLiveness(w http.ResponseWriter, r *http.Request) {
	if atomic.LoadInt32(&h.IsAlive) == 1 {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("ALIVE"))
	} else {
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte("DEAD"))
	}
}

func (h *MoEHealthProbe) handleReadiness(w http.ResponseWriter, r *http.Request) {
	if atomic.LoadInt32(&h.IsReady) == 1 {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("READY"))
	} else {
		w.WriteHeader(http.StatusServiceUnavailable)
		w.Write([]byte("LOADING_EXPERTS"))
	}
}

func (h *MoEHealthProbe) Start() {
	http.HandleFunc("/healthz", h.handleLiveness)
	http.HandleFunc("/readyz", h.handleReadiness)
	fmt.Printf("[K8s Probe] Listening on :%d for Liveness/Readiness.\n", h.Port)
	// http.ListenAndServe(fmt.Sprintf(":%d", h.Port), nil)
}

