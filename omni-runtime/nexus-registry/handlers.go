// ============================================================
// 🌐 OMNI-NEXUS: HTTP API Handlers
// ============================================================
// REST API endpoints untuk package registry OMNI.
// Semua endpoint mengembalikan JSON format standar.
// ============================================================

package main

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"
)

// Handlers mengandung semua HTTP handler dengan akses ke storage
type Handlers struct {
	storage   *Storage
	startTime time.Time
}

// NewHandlers membuat instance handlers baru
func NewHandlers(storage *Storage) *Handlers {
	return &Handlers{
		storage:   storage,
		startTime: time.Now(),
	}
}

// ============================================================
// API Routes
// ============================================================

// HandleRegistry — GET /api/registry
// Mengembalikan informasi dan statistik registry
func (h *Handlers) HandleRegistry(w http.ResponseWriter, r *http.Request) {
	stats := h.storage.Stats()
	stats.UptimeSeconds = int64(time.Since(h.startTime).Seconds())

	respondJSON(w, 200, APIResponse{
		Success: true,
		Data: map[string]interface{}{
			"name":    "OMNI-NEXUS Registry",
			"version": "1.0.0",
			"url":     "https://nexus.omniframework.dev",
			"stats":   stats,
		},
	})
}

// HandlePublish — POST /api/packages
// Mempublikasikan package baru ke registry
func (h *Handlers) HandlePublish(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		respondJSON(w, 405, APIResponse{Success: false, Error: "Method not allowed"})
		return
	}

	var req PublishRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondJSON(w, 400, APIResponse{Success: false, Error: "Invalid JSON: " + err.Error()})
		return
	}

	// Decode tarball dari base64
	tarballData, err := base64.StdEncoding.DecodeString(req.Tarball)
	if err != nil {
		respondJSON(w, 400, APIResponse{Success: false, Error: "Invalid tarball encoding"})
		return
	}

	meta, err := h.storage.Publish(req, tarballData)
	if err != nil {
		respondJSON(w, 409, APIResponse{Success: false, Error: err.Error()})
		return
	}

	fmt.Printf("[NEXUS] 📦 Published: %s@%s (%d bytes)\n", meta.Name, meta.Version, meta.Size)
	respondJSON(w, 201, APIResponse{
		Success: true,
		Message: fmt.Sprintf("Package %s@%s berhasil dipublish", meta.Name, meta.Version),
		Data:    meta,
	})
}

// HandleGetPackage — GET /api/packages/{name}
// Mengembalikan info lengkap sebuah package (semua versi)
func (h *Handlers) HandleGetPackage(w http.ResponseWriter, r *http.Request) {
	name := extractPathParam(r.URL.Path, "/api/packages/")
	if name == "" || strings.Contains(name, "/") {
		respondJSON(w, 400, APIResponse{Success: false, Error: "Nama package diperlukan"})
		return
	}

	info, err := h.storage.GetPackage(name)
	if err != nil {
		respondJSON(w, 404, APIResponse{Success: false, Error: err.Error()})
		return
	}

	respondJSON(w, 200, APIResponse{Success: true, Data: info})
}

// HandleGetVersion — GET /api/packages/{name}/{version}
// Mengembalikan metadata satu versi spesifik
func (h *Handlers) HandleGetVersion(w http.ResponseWriter, r *http.Request) {
	parts := extractVersionParts(r.URL.Path)
	if len(parts) != 2 {
		respondJSON(w, 400, APIResponse{Success: false, Error: "Format: /api/packages/{name}/{version}"})
		return
	}

	meta, err := h.storage.GetVersion(parts[0], parts[1])
	if err != nil {
		respondJSON(w, 404, APIResponse{Success: false, Error: err.Error()})
		return
	}

	respondJSON(w, 200, APIResponse{Success: true, Data: meta})
}

// HandleDownload — GET /api/download/{name}/{version}
// Mengembalikan tarball package untuk diinstal
func (h *Handlers) HandleDownload(w http.ResponseWriter, r *http.Request) {
	path := strings.TrimPrefix(r.URL.Path, "/api/download/")
	parts := strings.SplitN(path, "/", 2)
	if len(parts) != 2 {
		respondJSON(w, 400, APIResponse{Success: false, Error: "Format: /api/download/{name}/{version}"})
		return
	}

	data, err := h.storage.GetTarball(parts[0], parts[1])
	if err != nil {
		respondJSON(w, 404, APIResponse{Success: false, Error: err.Error()})
		return
	}

	w.Header().Set("Content-Type", "application/gzip")
	w.Header().Set("Content-Disposition",
		fmt.Sprintf("attachment; filename=%s-%s.tar.gz", parts[0], parts[1]))
	w.Write(data)
}

// HandleSearch — GET /api/search?q={query}
// Mencari package berdasarkan nama atau deskripsi
func (h *Handlers) HandleSearch(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("q")
	if query == "" {
		// Tanpa query = list semua
		packages := h.storage.ListAll()
		respondJSON(w, 200, APIResponse{
			Success: true,
			Data: SearchResult{
				Total:    len(packages),
				Query:    "*",
				Packages: packages,
			},
		})
		return
	}

	result := h.storage.Search(query)
	respondJSON(w, 200, APIResponse{Success: true, Data: result})
}

// ============================================================
// Helper Functions
// ============================================================

func respondJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("X-Powered-By", "OMNI-NEXUS/1.0")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}

func extractPathParam(path, prefix string) string {
	return strings.TrimPrefix(path, prefix)
}

func extractVersionParts(path string) []string {
	trimmed := strings.TrimPrefix(path, "/api/packages/")
	parts := strings.SplitN(trimmed, "/", 2)
	if len(parts) == 2 && parts[0] != "" && parts[1] != "" {
		return parts
	}
	return nil
}
