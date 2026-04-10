// ============================================================
// 💾 OMNI-NEXUS: Package Storage Engine
// ============================================================
// Menyimpan metadata dan tarball package ke filesystem lokal.
// Struktur: registry_data/{package_name}/{version}/
// ============================================================

package main

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"time"
)

// Storage mengelola penyimpanan package di filesystem
type Storage struct {
	mu       sync.RWMutex
	basePath string
	index    map[string]*PackageInfo // in-memory index
}

// NewStorage membuat storage baru di path tertentu
func NewStorage(basePath string) *Storage {
	os.MkdirAll(basePath, 0755)
	s := &Storage{
		basePath: basePath,
		index:    make(map[string]*PackageInfo),
	}
	s.loadIndex()
	return s
}

// Publish menyimpan package baru ke storage
func (s *Storage) Publish(req PublishRequest, tarballData []byte) (*PackageMeta, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Validasi nama package
	if req.Name == "" || req.Version == "" {
		return nil, fmt.Errorf("nama dan versi package wajib diisi")
	}

	// Cek apakah versi sudah ada
	if info, exists := s.index[req.Name]; exists {
		for _, v := range info.Versions {
			if v.Version == req.Version {
				return nil, fmt.Errorf("versi %s@%s sudah terpublish", req.Name, req.Version)
			}
		}
	}

	// Hitung checksum
	hash := sha256.Sum256(tarballData)
	checksum := fmt.Sprintf("%x", hash)

	// Simpan tarball ke disk
	pkgDir := filepath.Join(s.basePath, req.Name, req.Version)
	os.MkdirAll(pkgDir, 0755)

	tarballPath := filepath.Join(pkgDir, fmt.Sprintf("%s-%s.tar.gz", req.Name, req.Version))
	if err := os.WriteFile(tarballPath, tarballData, 0644); err != nil {
		return nil, fmt.Errorf("gagal menyimpan tarball: %w", err)
	}

	// Buat metadata
	meta := &PackageMeta{
		Name:        req.Name,
		Version:     req.Version,
		Description: req.Description,
		Authors:     req.Authors,
		License:     req.License,
		Homepage:    req.Homepage,
		Repository:  req.Repository,
		Keywords:    req.Keywords,
		Edition:     req.Edition,
		Checksum:    checksum,
		Size:        int64(len(tarballData)),
		PublishedAt: time.Now(),
		Downloads:   0,
		Deps:        req.Deps,
	}

	// Simpan metadata JSON
	metaJSON, _ := json.MarshalIndent(meta, "", "  ")
	metaPath := filepath.Join(pkgDir, "meta.json")
	os.WriteFile(metaPath, metaJSON, 0644)

	// Update in-memory index
	version := PackageVersion{
		Version:     req.Version,
		Checksum:    checksum,
		Size:        int64(len(tarballData)),
		PublishedAt: time.Now(),
	}

	if info, exists := s.index[req.Name]; exists {
		info.Versions = append(info.Versions, version)
		info.Latest = req.Version
	} else {
		s.index[req.Name] = &PackageInfo{
			Name:        req.Name,
			Description: req.Description,
			Authors:     req.Authors,
			License:     req.License,
			Latest:      req.Version,
			Versions:    []PackageVersion{version},
			CreatedAt:   time.Now(),
		}
	}

	s.saveIndex()
	return meta, nil
}

// GetPackage mengembalikan info lengkap sebuah package
func (s *Storage) GetPackage(name string) (*PackageInfo, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	info, exists := s.index[name]
	if !exists {
		return nil, fmt.Errorf("package '%s' tidak ditemukan", name)
	}
	return info, nil
}

// GetVersion mengembalikan metadata satu versi
func (s *Storage) GetVersion(name, version string) (*PackageMeta, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	metaPath := filepath.Join(s.basePath, name, version, "meta.json")
	data, err := os.ReadFile(metaPath)
	if err != nil {
		return nil, fmt.Errorf("versi %s@%s tidak ditemukan", name, version)
	}

	var meta PackageMeta
	json.Unmarshal(data, &meta)
	return &meta, nil
}

// GetTarball membaca tarball file untuk download
func (s *Storage) GetTarball(name, version string) ([]byte, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	tarballPath := filepath.Join(s.basePath, name, version,
		fmt.Sprintf("%s-%s.tar.gz", name, version))
	data, err := os.ReadFile(tarballPath)
	if err != nil {
		return nil, fmt.Errorf("tarball %s@%s tidak ditemukan", name, version)
	}

	// Increment download counter
	if info, exists := s.index[name]; exists {
		info.TotalDL++
		for i, v := range info.Versions {
			if v.Version == version {
				info.Versions[i].Downloads++
				break
			}
		}
		s.saveIndex()
	}

	return data, nil
}

// Search mencari packages berdasarkan query string
func (s *Storage) Search(query string) *SearchResult {
	s.mu.RLock()
	defer s.mu.RUnlock()

	query = strings.ToLower(query)
	result := &SearchResult{
		Query:    query,
		Packages: make([]PackageMeta, 0),
	}

	for name, info := range s.index {
		if strings.Contains(strings.ToLower(name), query) ||
			strings.Contains(strings.ToLower(info.Description), query) {
			// Ambil metadata versi terbaru
			meta, err := s.getLatestMeta(name)
			if err == nil {
				result.Packages = append(result.Packages, *meta)
			}
		}
	}

	// Sort by name
	sort.Slice(result.Packages, func(i, j int) bool {
		return result.Packages[i].Name < result.Packages[j].Name
	})

	result.Total = len(result.Packages)
	return result
}

// ListAll mengembalikan semua packages
func (s *Storage) ListAll() []PackageMeta {
	s.mu.RLock()
	defer s.mu.RUnlock()

	packages := make([]PackageMeta, 0, len(s.index))
	for name := range s.index {
		meta, err := s.getLatestMeta(name)
		if err == nil {
			packages = append(packages, *meta)
		}
	}

	sort.Slice(packages, func(i, j int) bool {
		return packages[i].Name < packages[j].Name
	})

	return packages
}

// Stats mengembalikan statistik registry
func (s *Storage) Stats() RegistryStats {
	s.mu.RLock()
	defer s.mu.RUnlock()

	stats := RegistryStats{
		TotalPackages: len(s.index),
	}

	for _, info := range s.index {
		stats.TotalVersions += len(info.Versions)
		stats.TotalDownloads += info.TotalDL
	}

	return stats
}

// ============================================================
// Internal Methods
// ============================================================

func (s *Storage) getLatestMeta(name string) (*PackageMeta, error) {
	info := s.index[name]
	if info == nil || len(info.Versions) == 0 {
		return nil, fmt.Errorf("no versions")
	}

	latest := info.Versions[len(info.Versions)-1]
	return &PackageMeta{
		Name:        info.Name,
		Version:     latest.Version,
		Description: info.Description,
		Authors:     info.Authors,
		License:     info.License,
		Checksum:    latest.Checksum,
		Size:        latest.Size,
		PublishedAt: latest.PublishedAt,
		Downloads:   info.TotalDL,
	}, nil
}

func (s *Storage) loadIndex() {
	indexPath := filepath.Join(s.basePath, "_index.json")
	data, err := os.ReadFile(indexPath)
	if err != nil {
		return // File belum ada, mulai dari kosong
	}
	json.Unmarshal(data, &s.index)
}

func (s *Storage) saveIndex() {
	indexPath := filepath.Join(s.basePath, "_index.json")
	data, _ := json.MarshalIndent(s.index, "", "  ")
	os.WriteFile(indexPath, data, 0644)
}
