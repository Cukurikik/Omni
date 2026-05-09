// moe_anomaly_dashboard_api.go — Domain / Web
// Layer: Domain / API — Anomaly & Injection Dashboard API
//
// The Prompt Sanitizer and Entropy Analyzers catch malicious injections
// and hallucinations. This Go API serves those flagged incidents directly
// to the Admin React Dashboard for manual review and IP banning.

package moe

import (
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"time"
)

type SecurityIncident struct {
	ID        string    `json:"id"`
	Type      string    `json:"type"` // "injection", "hallucination", "pii_leak"
	TenantID  string    `json:"tenant_id"`
	Prompt    string    `json:"prompt_snippet"`
	ExpertID  int       `json:"expert_id"`
	Timestamp time.Time `json:"timestamp"`
}

type IncidentStore struct {
	incidents []SecurityIncident
	mu        sync.RWMutex
}

var globalIncidentStore = &IncidentStore{incidents: make([]SecurityIncident, 0)}

func LogIncident(incidentType, tenantID, prompt string, expertID int) {
	globalIncidentStore.mu.Lock()
	defer globalIncidentStore.mu.Unlock()

	globalIncidentStore.incidents = append(globalIncidentStore.incidents, SecurityIncident{
		ID:        fmt.Sprintf("INC-%d", time.Now().UnixNano()),
		Type:      incidentType,
		TenantID:  tenantID,
		Prompt:    prompt,
		ExpertID:  expertID,
		Timestamp: time.Now().UTC(),
	})
	fmt.Printf("[Security API] Logged %s incident from Tenant %s\n", incidentType, tenantID)
}

func GetIncidentsHandler(w http.ResponseWriter, r *http.Request) {
	globalIncidentStore.mu.RLock()
	defer globalIncidentStore.mu.RUnlock()

	// Return top 50 recent incidents
	limit := 50
	if len(globalIncidentStore.incidents) < limit {
		limit = len(globalIncidentStore.incidents)
	}

	recent := globalIncidentStore.incidents[len(globalIncidentStore.incidents)-limit:]

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(recent)
}

func InitAnomalyAPI() {
	// http.HandleFunc("/api/v1/admin/incidents", GetIncidentsHandler)
	fmt.Println("[Security API] Initialized Anomaly Dashboard REST Endpoints.")
}
