package routes

import (
	"net/http"

	"omnitools/core"
)

// JobStatusHandler membalas status terkini dari sebuah tugas
func JobStatusHandler(w http.ResponseWriter, r *http.Request) {
	jobID := r.URL.Query().Get("job_id")
	w.Header().Set("Content-Type", "application/json")

	// Cari di Antrean RAM atau WAL
	// (Untuk penyederhanaan, kita umpamakan Anda menyimpannya di map sementara atau mengambil dari Firestore)
	status := "PROCESSING"

	// Jika OMNI-DB (Firebase) aktif, langsung baca dari Firestore!
	if core.OmniDB != nil {
		doc, err := core.OmniDB.Collection("OmniJobs").Doc(jobID).Get(core.FireCtx)
		if err == nil && doc.Exists() {
			if s, ok := doc.Data()["status"].(string); ok {
				status = s
			}
		}
	}

	w.Write([]byte(`{"job_id": "` + jobID + `", "status": "` + status + `"}`))
}
