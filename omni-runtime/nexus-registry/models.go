// ============================================================
// 📦 OMNI-NEXUS: Data Models
// ============================================================
// Struktur data inti untuk package registry OMNI.
// ============================================================

package main

import "time"

// PackageMeta menyimpan metadata satu package yang terpublish
type PackageMeta struct {
	Name        string            `json:"name"`
	Version     string            `json:"version"`
	Description string            `json:"description"`
	Authors     []string          `json:"authors"`
	License     string            `json:"license"`
	Homepage    string            `json:"homepage,omitempty"`
	Repository  string            `json:"repository,omitempty"`
	Keywords    []string          `json:"keywords"`
	Edition     string            `json:"edition"`
	Checksum    string            `json:"checksum"`
	Size        int64             `json:"size"`
	PublishedAt time.Time         `json:"published_at"`
	Downloads   int64             `json:"downloads"`
	Deps        map[string]string `json:"dependencies,omitempty"`
}

// PackageVersion menyimpan data satu versi package
type PackageVersion struct {
	Version     string    `json:"version"`
	Checksum    string    `json:"checksum"`
	Size        int64     `json:"size"`
	PublishedAt time.Time `json:"published_at"`
	Downloads   int64     `json:"downloads"`
}

// PackageInfo adalah view detail sebuah package (semua versi)
type PackageInfo struct {
	Name        string           `json:"name"`
	Description string           `json:"description"`
	Authors     []string         `json:"authors"`
	License     string           `json:"license"`
	Latest      string           `json:"latest_version"`
	Versions    []PackageVersion `json:"versions"`
	TotalDL     int64            `json:"total_downloads"`
	CreatedAt   time.Time        `json:"created_at"`
}

// SearchResult adalah hasil pencarian package
type SearchResult struct {
	Total    int           `json:"total"`
	Query    string        `json:"query"`
	Packages []PackageMeta `json:"packages"`
}

// PublishRequest adalah payload dari `omni publish`
type PublishRequest struct {
	Name        string            `json:"name"`
	Version     string            `json:"version"`
	Description string            `json:"description"`
	Authors     []string          `json:"authors"`
	License     string            `json:"license"`
	Homepage    string            `json:"homepage,omitempty"`
	Repository  string            `json:"repository,omitempty"`
	Keywords    []string          `json:"keywords,omitempty"`
	Edition     string            `json:"edition,omitempty"`
	Deps        map[string]string `json:"dependencies,omitempty"`
	Tarball     string            `json:"tarball"` // base64 encoded
}

// APIResponse adalah format response standar
type APIResponse struct {
	Success bool        `json:"success"`
	Message string      `json:"message,omitempty"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

// RegistryStats menampilkan statistik registry
type RegistryStats struct {
	TotalPackages  int   `json:"total_packages"`
	TotalVersions  int   `json:"total_versions"`
	TotalDownloads int64 `json:"total_downloads"`
	UptimeSeconds  int64 `json:"uptime_seconds"`
}
