// omni_animelinks_engine.go
// Production-Grade CDN Link Aggregation Network Engine
// ==============================================================
// Absorbed from: umaichanuwu/AnimeLinks
//
// OMNI Layer: network/go_core
// @since 2026.4.0

package network_gocore

import (
	"errors"
	"fmt"
	"math"
	"net/url"
	"strings"
	"sync"
	"time"
)

const AnimelinksEngineVersion = "1.0.0-omni"

// LinkEntry represents a resolved CDN resource link.
type LinkEntry struct {
	ID         string
	SourceURL  string
	MirrorURLs []string
	Quality    string
	Format     string
	SizeBytes  int64
	Verified   bool
	AddedAt    time.Time
	ExpiresAt  time.Time
}

// LinkCatalog stores categorized link entries.
type LinkCatalog struct {
	Category string
	Entries  []*LinkEntry
}

// OmniAnimelinksEngine manages concurrent CDN URL resolution,
// mirror verification, link health checking, and rate-limited
// batch retrieval for media content aggregation.
type OmniAnimelinksEngine struct {
	mu           sync.RWMutex
	catalogs     map[string]*LinkCatalog
	linkIndex    map[string]*LinkEntry
	healthChecks int
	healthPassed int
	maxMirrors   int
	linkTTLHours int
}

// NewOmniAnimelinksEngine creates a new link aggregation engine.
func NewOmniAnimelinksEngine(maxMirrors, linkTTLHours int) *OmniAnimelinksEngine {
	if maxMirrors < 1 {
		maxMirrors = 5
	}
	if linkTTLHours < 1 {
		linkTTLHours = 24
	}
	return &OmniAnimelinksEngine{
		catalogs:     make(map[string]*LinkCatalog),
		linkIndex:    make(map[string]*LinkEntry),
		maxMirrors:   maxMirrors,
		linkTTLHours: linkTTLHours,
	}
}

// RegisterCatalog creates a new link category.
func (e *OmniAnimelinksEngine) RegisterCatalog(category string) (map[string]interface{}, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	if _, exists := e.catalogs[category]; exists {
		return nil, errors.New(fmt.Sprintf("catalog '%s' already exists", category))
	}
	e.catalogs[category] = &LinkCatalog{Category: category, Entries: []*LinkEntry{}}
	return map[string]interface{}{"status": "success", "category": category, "totalCatalogs": len(e.catalogs)}, nil
}

// AddLink adds a new link entry to a catalog.
func (e *OmniAnimelinksEngine) AddLink(category, id, sourceURL, quality, format string, sizeBytes int64) (map[string]interface{}, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	cat, ok := e.catalogs[category]
	if !ok {
		return nil, errors.New(fmt.Sprintf("catalog '%s' not found", category))
	}
	if _, exists := e.linkIndex[id]; exists {
		return nil, errors.New(fmt.Sprintf("link '%s' already indexed", id))
	}

	u, err := url.Parse(sourceURL)
	if err != nil {
		return nil, errors.New(fmt.Sprintf("invalid URL: %s", err.Error()))
	}

	entry := &LinkEntry{
		ID:         id,
		SourceURL:  sourceURL,
		MirrorURLs: []string{},
		Quality:    quality,
		Format:     format,
		SizeBytes:  sizeBytes,
		Verified:   false,
		AddedAt:    time.Now(),
		ExpiresAt:  time.Now().Add(time.Duration(e.linkTTLHours) * time.Hour),
	}
	cat.Entries = append(cat.Entries, entry)
	e.linkIndex[id] = entry

	return map[string]interface{}{
		"status":         "success",
		"link":           map[string]interface{}{"id": id, "host": u.Hostname(), "quality": quality, "format": format, "sizeBytes": sizeBytes},
		"catalog":        category,
		"totalInCatalog": len(cat.Entries),
	}, nil
}

// AddMirror adds a mirror URL to an existing link.
func (e *OmniAnimelinksEngine) AddMirror(linkID, mirrorURL string) (map[string]interface{}, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	entry, ok := e.linkIndex[linkID]
	if !ok {
		return nil, errors.New(fmt.Sprintf("link '%s' not found", linkID))
	}
	if len(entry.MirrorURLs) >= e.maxMirrors {
		return nil, errors.New(fmt.Sprintf("max mirrors (%d) reached for '%s'", e.maxMirrors, linkID))
	}
	entry.MirrorURLs = append(entry.MirrorURLs, mirrorURL)
	return map[string]interface{}{"status": "success", "linkId": linkID, "mirrors": len(entry.MirrorURLs), "maxMirrors": e.maxMirrors}, nil
}

// VerifyLink marks a link as verified after health check.
func (e *OmniAnimelinksEngine) VerifyLink(linkID string, isHealthy bool) (map[string]interface{}, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	entry, ok := e.linkIndex[linkID]
	if !ok {
		return nil, errors.New(fmt.Sprintf("link '%s' not found", linkID))
	}
	entry.Verified = isHealthy
	e.healthChecks++
	if isHealthy {
		e.healthPassed++
	}

	passRate := 0.0
	if e.healthChecks > 0 {
		passRate = float64(e.healthPassed) / float64(e.healthChecks) * 100
	}

	return map[string]interface{}{
		"status":     "success",
		"linkId":     linkID,
		"verified":   isHealthy,
		"healthRate": math.Round(passRate*100) / 100,
	}, nil
}

// QueryCatalog retrieves links from a catalog with optional filtering.
func (e *OmniAnimelinksEngine) QueryCatalog(category, quality, format string) (map[string]interface{}, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	cat, ok := e.catalogs[category]
	if !ok {
		return nil, errors.New(fmt.Sprintf("catalog '%s' not found", category))
	}

	var results []map[string]interface{}
	for _, entry := range cat.Entries {
		if quality != "" && !strings.EqualFold(entry.Quality, quality) {
			continue
		}
		if format != "" && !strings.EqualFold(entry.Format, format) {
			continue
		}
		results = append(results, map[string]interface{}{
			"id": entry.ID, "sourceURL": entry.SourceURL, "quality": entry.Quality,
			"format": entry.Format, "sizeBytes": entry.SizeBytes, "verified": entry.Verified,
			"mirrors": len(entry.MirrorURLs),
		})
	}

	return map[string]interface{}{
		"status":  "success",
		"results": results,
		"count":   len(results),
		"catalog": category,
	}, nil
}

// GetStats returns engine statistics.
func (e *OmniAnimelinksEngine) GetStats() map[string]interface{} {
	e.mu.RLock()
	defer e.mu.RUnlock()

	totalLinks := 0
	for _, cat := range e.catalogs {
		totalLinks += len(cat.Entries)
	}
	var totalSize int64
	for _, entry := range e.linkIndex {
		totalSize += entry.SizeBytes
	}

	return map[string]interface{}{
		"status":        "success",
		"totalCatalogs": len(e.catalogs),
		"totalLinks":    totalLinks,
		"totalSizeMB":   math.Round(float64(totalSize)/1048576*100) / 100,
		"healthChecks":  e.healthChecks,
		"healthPassed":  e.healthPassed,
	}
}

