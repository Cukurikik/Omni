package core

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"sync"
	"time"

	"cloud.google.com/go/firestore"
)

// ==========================================
// 🗄️ OMNI-DB: DATABASE AGNOSTIC INTERFACE
// ==========================================
// Kita hancurkan monopoli vendor database. Jenderal Golang sekarang
// menggunakan Interface murni. Developer bebas menyambungkan
// PostgreSQL, MongoDB, Firebase, atau LocalWAL hanya dengan
// mengubah SATU kata di appconfig.json → "database.engine".
//
// Filosofi: Kedaulatan Universal
//   Developer TIDAK BOLEH terkunci oleh vendor manapun.
//   Engine diganti tanpa mengubah satu baris aplikasi pun.
// ==========================================

// OmniDatabase adalah kontrak Hukum Alam yang harus dipatuhi
// oleh SETIAP implementasi database di alam semesta OMNI.
type OmniDatabase interface {
	// SaveJob menyimpan rekaman job baru ke database
	SaveJob(record JobRecord) error
	// GetJob mengambil rekaman job berdasarkan ID
	GetJob(jobID string) (JobRecord, error)
	// UpdateJob memperbarui field-field tertentu dari sebuah job
	UpdateJob(jobID string, fields map[string]interface{}) error
	// DeleteJob menghapus rekaman job berdasarkan ID
	DeleteJob(jobID string) error
	// ListJobs mengambil N rekaman job terbaru
	ListJobs(limit int) ([]JobRecord, error)
	// Ping memverifikasi koneksi ke database masih hidup
	Ping() error
	// Close menutup koneksi database (graceful shutdown)
	Close() error
}

// DB adalah pointer global ke Database Aktif.
// Seluruh kode OMNI memanggil: core.DB.SaveJob(...), core.DB.GetJob(...)
// tanpa peduli apakah di baliknya PostgreSQL, Firebase, atau LocalWAL.
var DB OmniDatabase

// InitDatabase membaca appconfig.json → database.engine, lalu otomatis
// menyambungkan ke implementasi yang tepat.
//
// Dipanggil SATU KALI di bootstrap.Ignite() setelah LoadAppConfig().
func InitDatabase() {
	if AppConfig == nil {
		log.Println("⚠️ [OMNI-DB] AppConfig belum dimuat! Fallback ke LocalWAL.")
		DB = NewLocalWAL()
		return
	}

	engine := AppConfig.Database.Engine
	log.Printf("🗄️ [OMNI-DB] Menginisialisasi Database Engine: %s", engine)

	switch engine {
	case "firebase":
		// Firebase Firestore sudah ditangani oleh firebase_db.go
		// OMNI-DB membungkusnya dengan adapter yang patuh pada interface
		DB = NewFirebaseAdapter()
		log.Println("✅ [OMNI-DB] Firebase Adapter terpasang. Kedaulatan terjaga.")

	case "postgres":
		// Placeholder — implementasi PostgreSQL connector via pgx
		log.Println("⚠️ [OMNI-DB] PostgreSQL connector belum terimplementasi penuh.")
		log.Println("   ℹ️  Fallback ke LocalWAL. Implementasi pgx akan datang di patch berikutnya.")
		DB = NewLocalWAL()

	case "local":
		DB = NewLocalWAL()
		log.Println("✅ [OMNI-DB] LocalWAL (Write-Ahead Log) terpasang. Zero dependency.")

	default:
		log.Printf("⚠️ [OMNI-DB] Engine '%s' tidak dikenali. Fallback ke LocalWAL.", engine)
		DB = NewLocalWAL()
	}
}

// ==========================================
// 🔥 FIREBASE ADAPTER: Membungkus OmniDB Firestore
// ==========================================
// Adapter ini mendelegasikan ke firebase_db.go (yang sudah ada)
// sambil mematuhi kontrak OmniDatabase interface.

type firebaseAdapter struct{}

func NewFirebaseAdapter() OmniDatabase {
	return &firebaseAdapter{}
}

func (f *firebaseAdapter) SaveJob(record JobRecord) error {
	if !IsFirebaseReady() {
		return fmt.Errorf("firebase belum terkoneksi")
	}
	RecordJobHistory(record)
	return nil
}

func (f *firebaseAdapter) GetJob(jobID string) (JobRecord, error) {
	if !IsFirebaseReady() {
		return JobRecord{}, fmt.Errorf("firebase belum terkoneksi")
	}
	doc, err := OmniDB.Collection("OmniJobs").Doc(jobID).Get(FireCtx)
	if err != nil {
		return JobRecord{}, err
	}
	var record JobRecord
	if err := doc.DataTo(&record); err != nil {
		return JobRecord{}, err
	}
	return record, nil
}

func (f *firebaseAdapter) UpdateJob(jobID string, fields map[string]interface{}) error {
	if !IsFirebaseReady() {
		return fmt.Errorf("firebase belum terkoneksi")
	}
	_, err := OmniDB.Collection("OmniJobs").Doc(jobID).Set(FireCtx, fields, firestore.MergeAll)
	return err
}

func (f *firebaseAdapter) DeleteJob(jobID string) error {
	if !IsFirebaseReady() {
		return fmt.Errorf("firebase belum terkoneksi")
	}
	_, err := OmniDB.Collection("OmniJobs").Doc(jobID).Delete(FireCtx)
	return err
}

func (f *firebaseAdapter) ListJobs(limit int) ([]JobRecord, error) {
	if !IsFirebaseReady() {
		return nil, fmt.Errorf("firebase belum terkoneksi")
	}
	iter := OmniDB.Collection("OmniJobs").OrderBy("created_at", firestore.Desc).Limit(limit).Documents(FireCtx)
	defer iter.Stop()

	var records []JobRecord
	for {
		doc, err := iter.Next()
		if err != nil {
			break
		}
		var rec JobRecord
		if err := doc.DataTo(&rec); err == nil {
			records = append(records, rec)
		}
	}
	return records, nil
}

func (f *firebaseAdapter) Ping() error {
	if !IsFirebaseReady() {
		return fmt.Errorf("firebase belum terkoneksi")
	}
	return nil
}

func (f *firebaseAdapter) Close() error {
	CloseFirebase()
	return nil
}

// ==========================================
// 💾 LOCAL-WAL: ZERO-DEPENDENCY FILE DATABASE
// ==========================================
// Write-Ahead Log berbasis file JSON untuk mode offline/standalone.
// Tidak membutuhkan PostgreSQL, Firebase, atau koneksi internet apapun.
// Data disimpan di: release/omni_wal/jobs.json

type localWAL struct {
	mu       sync.RWMutex
	jobs     map[string]JobRecord
	walPath  string
	modified bool
}

func NewLocalWAL() OmniDatabase {
	walDir := filepath.Join("..", "release", "omni_wal")
	os.MkdirAll(walDir, 0755)

	walPath := filepath.Join(walDir, "jobs.json")
	wal := &localWAL{
		jobs:    make(map[string]JobRecord),
		walPath: walPath,
	}

	// Muat data yang sudah ada (jika file ada)
	wal.loadFromDisk()

	// Background flush: tulis ke disk setiap 30 detik jika ada perubahan
	go wal.autoFlush()

	log.Printf("💾 [LOCAL-WAL] Database file aktif di: %s", walPath)
	return wal
}

func (w *localWAL) SaveJob(record JobRecord) error {
	w.mu.Lock()
	defer w.mu.Unlock()

	if record.CreatedAt == 0 {
		record.CreatedAt = time.Now().Unix()
	}
	w.jobs[record.JobID] = record
	w.modified = true
	return nil
}

func (w *localWAL) GetJob(jobID string) (JobRecord, error) {
	w.mu.RLock()
	defer w.mu.RUnlock()

	rec, ok := w.jobs[jobID]
	if !ok {
		return JobRecord{}, fmt.Errorf("job %s tidak ditemukan", jobID)
	}
	return rec, nil
}

func (w *localWAL) UpdateJob(jobID string, fields map[string]interface{}) error {
	w.mu.Lock()
	defer w.mu.Unlock()

	rec, ok := w.jobs[jobID]
	if !ok {
		return fmt.Errorf("job %s tidak ditemukan untuk diupdate", jobID)
	}

	// Update field yang diberikan
	if v, ok := fields["status"]; ok {
		rec.Status = v.(string)
	}
	if v, ok := fields["output_file"]; ok {
		rec.OutputFile = v.(string)
	}
	if v, ok := fields["error"]; ok {
		rec.Error = v.(string)
	}
	if v, ok := fields["finished_at"]; ok {
		rec.FinishedAt = v.(int64)
	}

	w.jobs[jobID] = rec
	w.modified = true
	return nil
}

func (w *localWAL) DeleteJob(jobID string) error {
	w.mu.Lock()
	defer w.mu.Unlock()

	delete(w.jobs, jobID)
	w.modified = true
	return nil
}

func (w *localWAL) ListJobs(limit int) ([]JobRecord, error) {
	w.mu.RLock()
	defer w.mu.RUnlock()

	records := make([]JobRecord, 0, len(w.jobs))
	for _, rec := range w.jobs {
		records = append(records, rec)
	}

	// Sederhana: ambil N terakhir (tanpa sorting untuk performa)
	if len(records) > limit {
		records = records[len(records)-limit:]
	}
	return records, nil
}

func (w *localWAL) Ping() error {
	return nil // LocalWAL selalu hidup
}

func (w *localWAL) Close() error {
	return w.flushToDisk()
}

// --- Internal Methods ---

func (w *localWAL) loadFromDisk() {
	data, err := os.ReadFile(w.walPath)
	if err != nil {
		return // File belum ada — fresh start
	}

	var records []JobRecord
	if err := json.Unmarshal(data, &records); err != nil {
		log.Printf("⚠️ [LOCAL-WAL] File WAL rusak, memulai database baru: %v", err)
		return
	}

	for _, rec := range records {
		w.jobs[rec.JobID] = rec
	}
	log.Printf("💾 [LOCAL-WAL] Dimuat %d rekaman job dari disk.", len(records))
}

func (w *localWAL) flushToDisk() error {
	w.mu.RLock()
	defer w.mu.RUnlock()

	records := make([]JobRecord, 0, len(w.jobs))
	for _, rec := range w.jobs {
		records = append(records, rec)
	}

	data, err := json.MarshalIndent(records, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(w.walPath, data, 0644)
}

func (w *localWAL) autoFlush() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		w.mu.RLock()
		needsFlush := w.modified
		w.mu.RUnlock()

		if needsFlush {
			if err := w.flushToDisk(); err != nil {
				log.Printf("⚠️ [LOCAL-WAL] Gagal flush ke disk: %v", err)
			} else {
				w.mu.Lock()
				w.modified = false
				w.mu.Unlock()
			}
		}
	}
}
