package middleware

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"time"

	"omnitools/services"
)

// ==========================================
// KONFIGURASI KARANTINA (Inovasi #1: Zero-RAM Streaming)
// ==========================================
const MaxUploadSize = 2 << 30      // 2 GB (naik dari 500 MB karena streaming)
const StreamBufferSize = 32 * 1024 // 32 KB — ukuran potongan streaming
const QuarantineDir = "../release/omni_quarantine/"
const CacheDir = "../release/omni_cache/"

// InitSandbox memastikan folder karantina dan cache terbentuk sebelum server menerima request
func InitSandbox() {
	dirs := []string{QuarantineDir, CacheDir}
	for _, dir := range dirs {
		if _, err := os.Stat(dir); os.IsNotExist(err) {
			os.MkdirAll(dir, os.ModePerm)
		}
	}
	services.WriteLog("SECURITY", "INFO_SANDBOX", "Direktori Penjara & Cache divalidasi dan dikunci!")
}

// sendQuarantineError mengirimkan respons error JSON sesuai Kontrak Universal
func sendQuarantineError(w http.ResponseWriter, code string, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusBadRequest)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": false,
		"layer":   "SECURITY_GATEWAY",
		"code":    code,
		"message": message,
	})
}

// ==========================================
// INOVASI #1: PIPA STREAMING FILE RAKSASA (Zero-RAM Upload)
// ==========================================
// Middleware ini TIDAK menggunakan r.ParseMultipartForm() yang memuat
// seluruh file ke RAM. Sebagai gantinya, ia menggunakan r.MultipartReader()
// yang membaca file sebesar 32 KB per potongan melalui io.CopyBuffer,
// langsung mengalirkannya ke disk karantina.
//
// EFEK: Upload file 10 GB hanya memakan RAM sebesar 32 KB!
func FileQuarantineHandler(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		// Batasi ukuran total body (proteksi terhadap upload tanpa batas)
		r.Body = http.MaxBytesReader(w, r.Body, MaxUploadSize)

		// ====== STREAMING MURNI (bukan ParseMultipartForm!) ======
		// Jika bukan multipart, loloskan langsung (mungkin tool yang tidak butuh file)
		reader, err := r.MultipartReader()
		if err != nil {
			r.Header.Set("X-Omni-Quarantine-Path", "")
			next.ServeHTTP(w, r)
			return
		}

		var safeFilePath string
		var originalExt string

		// Iterasi setiap bagian (part) dari multipart stream
		for {
			part, partErr := reader.NextPart()
			if partErr == io.EOF {
				break // Semua part sudah dibaca
			}
			if partErr != nil {
				sendQuarantineError(w, "ERR_STREAM_READ", "Gagal membaca stream multipart.")
				return
			}

			// Kita hanya tertarik pada field bernama "omni_file"
			if part.FormName() != "omni_file" {
				part.Close()
				continue
			}

			// Ambil ekstensi dari nama file asli
			originalExt = filepath.Ext(part.FileName())

			// ====== VALIDASI MAGIC BYTES (Baca 512 byte pertama saja) ======
			magicBuf := make([]byte, 512)
			n, _ := io.ReadAtLeast(part, magicBuf, 1)
			if n == 0 {
				part.Close()
				sendQuarantineError(w, "ERR_EMPTY_FILE", "File kosong.")
				return
			}
			filetype := http.DetectContentType(magicBuf[:n])

			// Whitelist format yang diizinkan
			allowedTypes := map[string]bool{
				"video/mp4":                true,
				"video/webm":               true,
				"video/x-matroska":         true,
				"audio/wav":                true,
				"audio/mpeg":               true,
				"audio/ogg":                true,
				"audio/flac":               true,
				"application/pdf":          true,
				"application/zip":          true,
				"image/png":                true,
				"image/jpeg":               true,
				"image/webp":               true,
				"text/plain":               true,
				"text/csv":                 true,
				"application/json":         true,
				"application/xml":          true,
				"text/xml":                 true,
				"application/octet-stream": true, // Fallback umum untuk file biner
			}

			if !allowedTypes[filetype] {
				part.Close()
				sendQuarantineError(w, "ERR_INVALID_FORMAT", fmt.Sprintf("Format '%s' dilarang oleh Magic Bytes Guard.", filetype))
				return
			}

			// ====== HASHING NAMA FILE (Amputasi nama asli) ======
			hashInput := fmt.Sprintf("%s-%d", part.FileName(), time.Now().UnixNano())
			hash := sha256.Sum256([]byte(hashInput))
			safeFileName := hex.EncodeToString(hash[:]) + originalExt
			safeFilePath = filepath.Join(QuarantineDir, safeFileName)

			// ====== STREAMING 32 KB ke DISK (Zero-RAM Core) ======
			dst, createErr := os.Create(safeFilePath)
			if createErr != nil {
				part.Close()
				sendQuarantineError(w, "ERR_SYSTEM_WRITE", "Sistem Isolasi Gagal membuat file.")
				return
			}

			// Tulis 512 byte Magic Bytes yang sudah dibaca tadi
			dst.Write(magicBuf[:n])

			// Alirkan SISA file sebanyak 32 KB per potongan
			// Ini adalah inti dari Zero-RAM Upload!
			streamBuf := make([]byte, StreamBufferSize) // Hanya 32 KB di RAM
			_, copyErr := io.CopyBuffer(dst, part, streamBuf)

			dst.Close()
			part.Close()

			if copyErr != nil {
				os.Remove(safeFilePath) // Bersihkan file rusak
				sendQuarantineError(w, "ERR_STREAM_COPY", "Streaming file terputus.")
				return
			}

			services.WriteLog("QUARANTINE", "INFO_STREAM_OK", fmt.Sprintf("File streaming selesai: %s (%s)", safeFileName, filetype))
			break // Hanya proses 1 file utama
		}

		if safeFilePath == "" {
			// Jika tidak ada "omni_file", mungkin itu alat sederhana yang tidak butuh input. Biarkan lolos.
			r.Header.Set("X-Omni-Quarantine-Path", "")
			next.ServeHTTP(w, r)
			return
		}

		// Sematkan path aman ke header internal agar handler berikutnya bisa membacanya
		r.Header.Set("X-Omni-Quarantine-Path", safeFilePath)

		// Lanjut ke handler berikutnya (audio_handler, pdf_handler, dll.)
		next.ServeHTTP(w, r)
	}
}
