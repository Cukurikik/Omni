package services

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"
)

// ==========================================
// 🛡️ OMNI SECURITY SCANNER (Phase 9)
// ==========================================
// Static Analysis Security Testing (SAST) bawaan OMNI.
// Memindai codebase dari pola-pola berbahaya tanpa dependensi eksternal.

// SecurityFinding adalah satu temuan keamanan
type SecurityFinding struct {
	Severity    string `json:"severity"`    // CRITICAL, HIGH, MEDIUM, LOW
	Category    string `json:"category"`    // SQL_INJECTION, XSS, HARDCODED_SECRET, dll
	File        string `json:"file"`
	Line        int    `json:"line"`
	Description string `json:"description"`
	Suggestion  string `json:"suggestion"`
}

// SecurityScanner menjalankan pemeriksaan keamanan statis
type SecurityScanner struct {
	rootDir  string
	findings []SecurityFinding
	patterns []scanPattern
}

type scanPattern struct {
	regex    *regexp.Regexp
	category string
	severity string
	desc     string
	fix      string
	fileExt  []string
}

// NewSecurityScanner membuat scanner baru
func NewSecurityScanner(rootDir string) *SecurityScanner {
	s := &SecurityScanner{
		rootDir:  rootDir,
		findings: make([]SecurityFinding, 0),
	}
	s.loadPatterns()
	return s
}

// loadPatterns memuat semua pola deteksi keamanan
func (s *SecurityScanner) loadPatterns() {
	s.patterns = []scanPattern{
		// Hardcoded Secrets
		{
			regex:    regexp.MustCompile(`(?i)(password|secret|api_key|token|private_key)\s*[:=]\s*["'][^"']{8,}["']`),
			category: "HARDCODED_SECRET",
			severity: "CRITICAL",
			desc:     "Rahasia ter-hardcode ditemukan dalam source code",
			fix:      "Gunakan environment variable atau Secret Manager",
			fileExt:  []string{".go", ".js", ".ts", ".py", ".mjs"},
		},
		// SQL Injection
		{
			regex:    regexp.MustCompile(`(?i)(fmt\.Sprintf|string\s*\+).*(?:SELECT|INSERT|UPDATE|DELETE|DROP)\s`),
			category: "SQL_INJECTION",
			severity: "HIGH",
			desc:     "Potensi SQL Injection: query dibangun dengan string concatenation",
			fix:      "Gunakan parameterized queries atau prepared statements",
			fileExt:  []string{".go"},
		},
		// Unsafe eval
		{
			regex:    regexp.MustCompile(`\beval\s*\(`),
			category: "CODE_INJECTION",
			severity: "CRITICAL",
			desc:     "Penggunaan eval() terdeteksi — vektor serangan Code Injection",
			fix:      "Hindari eval(). Gunakan JSON.parse() atau parser aman",
			fileExt:  []string{".js", ".ts", ".mjs"},
		},
		// Unencrypted HTTP
		{
			regex:    regexp.MustCompile(`http://[a-zA-Z0-9.-]+`),
			category: "INSECURE_TRANSPORT",
			severity: "MEDIUM",
			desc:     "Koneksi HTTP tidak terenkripsi ke server eksternal",
			fix:      "Gunakan HTTPS untuk semua koneksi eksternal",
			fileExt:  []string{".go", ".js", ".ts", ".mjs", ".py"},
		},
		// Console.log in production
		{
			regex:    regexp.MustCompile(`console\.(log|debug|trace)\(`),
			category: "INFO_LEAK",
			severity: "LOW",
			desc:     "console.log() ditemukan — potensi kebocoran info di produksi",
			fix:      "Gunakan structured logger (omni-log) untuk produksi",
			fileExt:  []string{".js", ".ts", ".mjs"},
		},
		// Unsafe pointer usage
		{
			regex:    regexp.MustCompile(`unsafe\.Pointer`),
			category: "UNSAFE_MEMORY",
			severity: "HIGH",
			desc:     "Penggunaan unsafe.Pointer — berisiko memory corruption",
			fix:      "Pertimbangkan alternatif safe. Jika diperlukan, tambahkan guard",
			fileExt:  []string{".go"},
		},
	}
}

// RunScan menjalankan pemindaian keamanan pada seluruh codebase
func (s *SecurityScanner) RunScan() ([]SecurityFinding, error) {
	log.Println("🛡️ [SECURITY SCANNER] Memulai pemindaian SAST...")
	startTime := time.Now()

	err := filepath.Walk(s.rootDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return nil // Skip file yang tidak bisa diakses
		}

		// Skip directories yang tidak relevan
		if info.IsDir() {
			base := filepath.Base(path)
			if base == "node_modules" || base == ".git" || base == "vendor" || base == ".venv" || base == "build" {
				return filepath.SkipDir
			}
			return nil
		}

		ext := filepath.Ext(path)
		data, err := os.ReadFile(path)
		if err != nil {
			return nil
		}

		lines := strings.Split(string(data), "\n")

		for _, pattern := range s.patterns {
			// Cek apakah ekstensi file cocok
			matched := false
			for _, e := range pattern.fileExt {
				if ext == e {
					matched = true
					break
				}
			}
			if !matched {
				continue
			}

			for i, line := range lines {
				if pattern.regex.MatchString(line) {
					relPath, _ := filepath.Rel(s.rootDir, path)
					s.findings = append(s.findings, SecurityFinding{
						Severity:    pattern.severity,
						Category:    pattern.category,
						File:        relPath,
						Line:        i + 1,
						Description: pattern.desc,
						Suggestion:  pattern.fix,
					})
				}
			}
		}
		return nil
	})

	if err != nil {
		return nil, fmt.Errorf("OMNI_SECURITY_ERROR: %w", err)
	}

	elapsed := time.Since(startTime)
	log.Printf("🛡️ [SECURITY SCANNER] Selesai dalam %.2fs — %d temuan", elapsed.Seconds(), len(s.findings))
	return s.findings, nil
}

// GetSummary menghasilkan ringkasan hasil scan
func (s *SecurityScanner) GetSummary() map[string]interface{} {
	critical, high, medium, low := 0, 0, 0, 0
	for _, f := range s.findings {
		switch f.Severity {
		case "CRITICAL":
			critical++
		case "HIGH":
			high++
		case "MEDIUM":
			medium++
		case "LOW":
			low++
		}
	}

	return map[string]interface{}{
		"total_findings": len(s.findings),
		"critical":       critical,
		"high":           high,
		"medium":         medium,
		"low":            low,
		"scanned_dir":    s.rootDir,
		"scanner":        "OMNI-SAST v1.0",
	}
}
