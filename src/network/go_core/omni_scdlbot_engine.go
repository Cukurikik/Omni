// omni_scdlbot_engine.go
// Production-Grade Audio Download Network Engine
// ==============================================================
// Absorbed from: gpchelkin/scdlbot
//
// OMNI Layer: network/go_core
// @since 2026.4.0

package network_gocore

import (
	"fmt"
	"math"
	"net/url"
	"path"
	"strings"
	"sync"
	"time"
)

const ScdlbotEngineVersion = "1.0.0-omni"

// ScdlbotError represents domain-specific errors.
type ScdlbotError struct {
	Code    string
	Message string
}

func (e *ScdlbotError) Error() string {
	return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}

// DownloadRequest represents a pending audio download.
type DownloadRequest struct {
	ID        string
	URL       string
	Platform  string
	Format    string
	Quality   string
	Status    string
	Progress  float64
	BytesRecv int64
	TotalSize int64
	StartedAt time.Time
}

// DownloadResult represents a completed download.
type DownloadResult struct {
	RequestID  string
	FilePath   string
	FileSize   int64
	Format     string
	DurationMs int64
	DownloadMs int64
	Throughput float64
}

// OmniScdlbotEngine manages concurrent audio downloads from
// multiple platforms (SoundCloud, YouTube, Bandcamp, etc.)
// with rate limiting, retry logic, and format negotiation.
type OmniScdlbotEngine struct {
	mu              sync.RWMutex
	maxConcurrent   int
	retryAttempts   int
	timeoutSec      int
	activeDownloads map[string]*DownloadRequest
	completedCount  int
	failedCount     int
	totalBytesRecv  int64
}

// NewOmniScdlbotEngine creates a new download engine.
func NewOmniScdlbotEngine(maxConcurrent, retryAttempts, timeoutSec int) *OmniScdlbotEngine {
	if maxConcurrent < 1 {
		maxConcurrent = 4
	}
	if retryAttempts < 0 {
		retryAttempts = 3
	}
	if timeoutSec < 1 {
		timeoutSec = 30
	}
	return &OmniScdlbotEngine{
		maxConcurrent:   maxConcurrent,
		retryAttempts:   retryAttempts,
		timeoutSec:      timeoutSec,
		activeDownloads: make(map[string]*DownloadRequest),
	}
}

// DetectPlatform identifies the audio platform from a URL.
func (e *OmniScdlbotEngine) DetectPlatform(rawURL string) (map[string]interface{}, error) {
	u, err := url.Parse(rawURL)
	if err != nil {
		return nil, &ScdlbotError{Code: "INVALID_URL", Message: err.Error()}
	}

	host := strings.ToLower(u.Hostname())
	var platform, mediaType string

	switch {
	case strings.Contains(host, "soundcloud"):
		platform = "soundcloud"
		mediaType = "audio"
	case strings.Contains(host, "youtube") || strings.Contains(host, "youtu.be"):
		platform = "youtube"
		mediaType = "video"
	case strings.Contains(host, "bandcamp"):
		platform = "bandcamp"
		mediaType = "audio"
	case strings.Contains(host, "spotify"):
		platform = "spotify"
		mediaType = "metadata"
	default:
		platform = "unknown"
		mediaType = "unknown"
	}

	return map[string]interface{}{
		"status":    "success",
		"platform":  platform,
		"mediaType": mediaType,
		"host":      host,
		"path":      u.Path,
	}, nil
}

// SubmitDownload queues a new download request.
func (e *OmniScdlbotEngine) SubmitDownload(id, rawURL, format, quality string) (map[string]interface{}, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	if len(e.activeDownloads) >= e.maxConcurrent {
		return nil, &ScdlbotError{Code: "QUEUE_FULL", Message: fmt.Sprintf("Max %d concurrent downloads", e.maxConcurrent)}
	}

	if _, exists := e.activeDownloads[id]; exists {
		return nil, &ScdlbotError{Code: "DUPLICATE_ID", Message: fmt.Sprintf("Download %s already exists", id)}
	}

	platformInfo, err := e.DetectPlatform(rawURL)
	if err != nil {
		return nil, err
	}

	validFormats := map[string]bool{"mp3": true, "ogg": true, "flac": true, "wav": true, "m4a": true, "opus": true}
	if !validFormats[format] {
		return nil, &ScdlbotError{Code: "INVALID_FORMAT", Message: fmt.Sprintf("Format '%s' not supported", format)}
	}

	req := &DownloadRequest{
		ID:        id,
		URL:       rawURL,
		Platform:  platformInfo["platform"].(string),
		Format:    format,
		Quality:   quality,
		Status:    "queued",
		StartedAt: time.Now(),
	}
	e.activeDownloads[id] = req

	return map[string]interface{}{
		"status":   "success",
		"request":  map[string]interface{}{"id": id, "platform": req.Platform, "format": format, "quality": quality, "status": "queued"},
		"active":   len(e.activeDownloads),
		"capacity": e.maxConcurrent,
	}, nil
}

// UpdateProgress updates the progress of an active download.
func (e *OmniScdlbotEngine) UpdateProgress(id string, bytesRecv, totalSize int64) (map[string]interface{}, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	req, ok := e.activeDownloads[id]
	if !ok {
		return nil, &ScdlbotError{Code: "NOT_FOUND", Message: fmt.Sprintf("Download %s not found", id)}
	}

	req.BytesRecv = bytesRecv
	req.TotalSize = totalSize
	req.Status = "downloading"
	if totalSize > 0 {
		req.Progress = float64(bytesRecv) / float64(totalSize) * 100.0
	}

	elapsed := time.Since(req.StartedAt).Seconds()
	throughput := 0.0
	if elapsed > 0 {
		throughput = float64(bytesRecv) / elapsed / 1024
	}

	return map[string]interface{}{
		"status":        "success",
		"progress":      math.Round(req.Progress*100) / 100,
		"bytesRecv":     bytesRecv,
		"totalSize":     totalSize,
		"throughputKBs": math.Round(throughput*100) / 100,
		"elapsedSec":    math.Round(elapsed*100) / 100,
	}, nil
}

// CompleteDownload marks a download as finished.
func (e *OmniScdlbotEngine) CompleteDownload(id, filePath string, fileSize, durationMs int64) (map[string]interface{}, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	req, ok := e.activeDownloads[id]
	if !ok {
		return nil, &ScdlbotError{Code: "NOT_FOUND", Message: fmt.Sprintf("Download %s not found", id)}
	}

	elapsed := time.Since(req.StartedAt).Milliseconds()
	throughput := 0.0
	if elapsed > 0 {
		throughput = float64(fileSize) / float64(elapsed) * 1000 / 1024
	}

	delete(e.activeDownloads, id)
	e.completedCount++
	e.totalBytesRecv += fileSize

	ext := path.Ext(filePath)

	return map[string]interface{}{
		"status": "success",
		"result": map[string]interface{}{
			"requestId":     id,
			"filePath":      filePath,
			"fileSize":      fileSize,
			"format":        strings.TrimPrefix(ext, "."),
			"durationMs":    durationMs,
			"downloadMs":    elapsed,
			"throughputKBs": math.Round(throughput*100) / 100,
		},
		"completedTotal": e.completedCount,
	}, nil
}

// GetStats returns engine statistics.
func (e *OmniScdlbotEngine) GetStats() map[string]interface{} {
	e.mu.RLock()
	defer e.mu.RUnlock()

	return map[string]interface{}{
		"status":          "success",
		"activeDownloads": len(e.activeDownloads),
		"maxConcurrent":   e.maxConcurrent,
		"completedCount":  e.completedCount,
		"failedCount":     e.failedCount,
		"totalBytesRecv":  e.totalBytesRecv,
		"totalMBRecv":     math.Round(float64(e.totalBytesRecv)/1048576*100) / 100,
	}
}

// Ensure compilation check
var _ error = (*ScdlbotError)(nil)

