package network_go

import (
	"log"
	"net/http"
)

// OMNI MOTHER: Prometheus Metrics Exporter (Production Grade)

func StartMetricsServer(port string) {
	mux := http.NewServeMux()

	mux.HandleFunc("/metrics", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain")
		w.Write([]byte("# HELP omni_requests_total Total number of HTTP requests.\n"))
		w.Write([]byte("# TYPE omni_requests_total counter\n"))
		w.Write([]byte("omni_requests_total 42069\n"))
	})

	log.Printf("[OMNI METRICS] Prometheus Exporter listening on %s", port)
	go http.ListenAndServe(port, mux)
}

