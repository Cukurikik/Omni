package core

import (
	"crypto/rand"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// ==========================================
// 📥 OMNI QUARANTINE: ZERO-RAM FILE STREAMING
// ==========================================
// Menangkap file raksasa (hingga 50GB) tanpa menyentuh RAM.
// Data mengalir langsung dari jaringan (Network Socket) → SSD.
// io.Copy hanya menggunakan buffer ~32KB meskipun filenya 50GB!
// ==========================================

const (
	MaxUploadSize  = 50 << 30 // 50GB dalam bytes
	QuarantineBase = "../release/omni_quarantine"
)

// UploadResult berisi informasi file yang berhasil di-quarantine
type UploadResult struct {
	FilePath     string `json:"file_path"`
	OriginalName string `json:"original_name"`
	Size         int64  `json:"size"`
	QuarantineID string `json:"quarantine_id"`
}

// generateQuarantineID membuat ID unik untuk setiap file yang masuk
func generateQuarantineID() string {
	b := make([]byte, 8)
	rand.Read(b)
	return fmt.Sprintf("QRN-%d-%x", time.Now().UnixNano(), b)
}

// sanitizeFilename membersihkan nama file dari karakter berbahaya
func sanitizeFilename(name string) string {
	// Hapus path traversal
	name = filepath.Base(name)
	// Hapus karakter berbahaya
	replacer := strings.NewReplacer(
		"..", "",
		"/", "",
		"\\", "",
		"\x00", "",
	)
	return replacer.Replace(name)
}

// StreamUpload menangkap file raksasa menggunakan streaming multipart reader.
// KUNCI: r.MultipartReader() TIDAK membaca seluruh body ke RAM
// seperti r.ParseMultipartForm() yang berbahaya.
//
// Alur: Network Socket → io.Copy (32KB buffer) → SSD File
//
// Parameter:
//   - r: HTTP Request dari client
//   - destFolder: Subfolder di dalam quarantine (opsional, default: root)
//
// Return: UploadResult dengan path file dan metadata
func StreamUpload(r *http.Request, destFolder string) (*UploadResult, error) {
	// 1. Batasi ukuran maksimal (50GB)
	r.Body = http.MaxBytesReader(nil, r.Body, MaxUploadSize)

	// 2. Baca multipart form menggunakan STREAMING reader
	// KUNCI: MultipartReader() vs ParseMultipartForm()
	// - MultipartReader() → Streaming, RAM ~32KB
	// - ParseMultipartForm() → Membaca SELURUH body ke RAM! HARAM!
	reader, err := r.MultipartReader()
	if err != nil {
		return nil, fmt.Errorf("gagal membaca multipart stream: %v", err)
	}

	// 3. Iterasi setiap bagian (part) dari multipart form
	for {
		part, err := reader.NextPart()
		if err == io.EOF {
			break // Semua part sudah dibaca
		}
		if err != nil {
			return nil, fmt.Errorf("gagal membaca part: %v", err)
		}

		// Cari field bernama "omni_file" (Fallback ke "file" untuk kompatibilitas)
		fieldName := part.FormName()
		if fieldName != "omni_file" && fieldName != "file" {
			part.Close()
			continue
		}

		// 4. Sanitasi nama file (Anti-Path-Traversal)
		originalName := sanitizeFilename(part.FileName())
		if originalName == "" || originalName == "." {
			part.Close()
			return nil, fmt.Errorf("nama file tidak valid: %s", part.FileName())
		}

		// 5. Siapkan zona karantina
		quarantineID := generateQuarantineID()
		quarantineDir := filepath.Join(QuarantineBase, destFolder)
		if err := os.MkdirAll(quarantineDir, 0755); err != nil {
			part.Close()
			return nil, fmt.Errorf("gagal membuat folder karantina: %v", err)
		}

		// Gunakan ID unik sebagai prefix untuk mencegah collision
		destPath := filepath.Join(quarantineDir, quarantineID+"_"+originalName)

		// 6. THE MAGIC: OMNI-TITAN (10GB Smart RAM Pool)
		// Mengalirkan data dari Network → RAM Buffer → SSD
		// Melindungi SSD dari keausan (TBW) dengan batch write raksasa!
		startTime := time.Now()
		written, copyErr := StreamUploadSmartBuffer(part, destPath)
		elapsed := time.Since(startTime)

		part.Close()

		if copyErr != nil {
			os.Remove(destPath) // Bersihkan file gagal
			return nil, fmt.Errorf("gagal streaming file ke SSD: %v", copyErr)
		}

		speedMBps := float64(written) / (1024 * 1024) / elapsed.Seconds()
		log.Printf("📥 [QUARANTINE] File diterima: %s (%d MB, %.1f MB/s) → %s",
			originalName, written/(1024*1024), speedMBps, destPath)

		return &UploadResult{
			FilePath:     destPath,
			OriginalName: originalName,
			Size:         written,
			QuarantineID: quarantineID,
		}, nil
	}

	return nil, fmt.Errorf("field 'omni_file' atau 'file' tidak ditemukan dalam request multipart")
}

// StreamUploadMultiple menangkap MULTIPLE files dari satu request.
// Berguna untuk fitur Batch Processor dan Video Merger.
func StreamUploadMultiple(r *http.Request, destFolder string) ([]*UploadResult, error) {
	r.Body = http.MaxBytesReader(nil, r.Body, MaxUploadSize)

	reader, err := r.MultipartReader()
	if err != nil {
		return nil, fmt.Errorf("gagal membaca multipart stream: %v", err)
	}

	var results []*UploadResult
	quarantineDir := filepath.Join(QuarantineBase, destFolder)
	if err := os.MkdirAll(quarantineDir, 0755); err != nil {
		return nil, fmt.Errorf("gagal membuat folder karantina: %v", err)
	}

	for {
		part, err := reader.NextPart()
		if err == io.EOF {
			break
		}
		if err != nil {
			return results, fmt.Errorf("gagal membaca part: %v", err)
		}

		fieldName := part.FormName()
		if fieldName != "omni_file" && fieldName != "file" && fieldName != "files" {
			part.Close()
			continue
		}

		originalName := sanitizeFilename(part.FileName())
		if originalName == "" || originalName == "." {
			part.Close()
			continue
		}

		quarantineID := generateQuarantineID()
		destPath := filepath.Join(quarantineDir, quarantineID+"_"+originalName)

		written, copyErr := StreamUploadSmartBuffer(part, destPath)
		part.Close()

		if copyErr != nil {
			os.Remove(destPath)
			continue
		}

		results = append(results, &UploadResult{
			FilePath:     destPath,
			OriginalName: originalName,
			Size:         written,
			QuarantineID: quarantineID,
		})
	}

	if len(results) == 0 {
		return nil, fmt.Errorf("tidak ada file yang berhasil diterima")
	}

	return results, nil
}
