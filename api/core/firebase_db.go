package core

import (
	"context"
	"log"
	"time"

	"cloud.google.com/go/firestore"
	firebase "firebase.google.com/go"
	"google.golang.org/api/option"
)

// ==========================================
// 🔥 OMNI-DB: Firebase Firestore Integration
// ==========================================
// Menyambungkan jantung Golang ke Google Cloud Firestore.
// Semua riwayat tugas (Job History) disimpan otomatis,
// dan React Frontend bisa membacanya secara REAL-TIME
// tanpa harus menembak endpoint Golang.
//
// Ini memangkas beban RAM server secara drastis karena
// traffic pembacaan data dialihkan ke peladen Google.
// ==========================================

var (
	// OmniDB adalah klien Firestore global — bisa dipanggil dari mana saja
	// Contoh: core.OmniDB.Collection("OmniJobs").Doc(id).Set(...)
	OmniDB  *firestore.Client
	FireCtx context.Context
)

// InitFirebase menyalakan koneksi ke Firebase Firestore.
// Dipanggil SATU KALI di main.go setelah LoadAppConfig.
func InitFirebase() {
	if AppConfig == nil || !AppConfig.Firebase.Enabled {
		log.Println("⚠️ [OMNI-DB] Firebase dinonaktifkan di AppConfig. Skipping...")
		return
	}

	log.Println("🔥 [OMNI-DB] Menginisialisasi Firebase Admin SDK...")
	FireCtx = context.Background()

	// Baca Service Account Key dari path di appconfig.json
	opt := option.WithCredentialsFile(AppConfig.Firebase.CredentialsPath)

	app, err := firebase.NewApp(FireCtx, nil, opt)
	if err != nil {
		log.Printf("❌ [OMNI-DB] Gagal menyambung ke Firebase: %v", err)
		log.Println("   ℹ️  Server tetap berjalan tanpa Firebase. Riwayat job tidak akan disimpan ke cloud.")
		return
	}

	// Buka gerbang Firestore
	client, err := app.Firestore(FireCtx)
	if err != nil {
		log.Printf("❌ [OMNI-DB] Gagal membuka Firestore: %v", err)
		log.Println("   ℹ️  Server tetap berjalan tanpa Firestore.")
		return
	}

	OmniDB = client
	log.Printf("✅ [OMNI-DB] Koneksi Firebase Firestore BERHASIL! (Project: %s)", AppConfig.Firebase.ProjectID)
}

// CloseFirebase menutup koneksi Firestore (dipanggil saat graceful shutdown)
func CloseFirebase() {
	if OmniDB != nil {
		OmniDB.Close()
		log.Println("🔥 [OMNI-DB] Koneksi Firestore ditutup.")
	}
}

// IsFirebaseReady mengecek apakah Firestore siap digunakan
func IsFirebaseReady() bool {
	return OmniDB != nil
}

// ==========================================
// 📋 JOB RECORD: Format Dokumen NoSQL
// ==========================================

// JobRecord adalah format dokumen yang disimpan ke Koleksi "OmniJobs" di Firestore
type JobRecord struct {
	JobID      string `firestore:"job_id"      json:"job_id"`
	ToolID     string `firestore:"tool_id"     json:"tool_id"`
	Status     string `firestore:"status"      json:"status"`
	InputFile  string `firestore:"input_file"  json:"input_file"`
	OutputFile string `firestore:"output_file" json:"output_file"`
	InputSize  int64  `firestore:"input_size"  json:"input_size"`
	Error      string `firestore:"error"       json:"error,omitempty"`
	CreatedAt  int64  `firestore:"created_at"  json:"created_at"`
	FinishedAt int64  `firestore:"finished_at" json:"finished_at"`
}

// ==========================================
// 💾 OPERASI DATABASE OTOMATIS
// ==========================================

// RecordJobHistory menyimpan riwayat eksekusi alat ke Koleksi "OmniJobs"
// Dipanggil otomatis oleh engine/handlers.go saat job selesai/gagal.
//
// Contoh:
//
//	core.RecordJobHistory(core.JobRecord{
//	    JobID:  "JOB-123",
//	    ToolID: "video_compressor",
//	    Status: "COMPLETED",
//	})
func RecordJobHistory(record JobRecord) {
	if OmniDB == nil {
		return // Firebase mati — lewati tanpa error
	}

	// Isi timestamp jika kosong
	if record.CreatedAt == 0 {
		record.CreatedAt = time.Now().Unix()
	}
	if record.FinishedAt == 0 {
		record.FinishedAt = time.Now().Unix()
	}

	// Simpan ke koleksi "OmniJobs" dengan Document ID = job_id
	_, err := OmniDB.Collection("OmniJobs").Doc(record.JobID).Set(FireCtx, record)
	if err != nil {
		log.Printf("⚠️ [OMNI-DB] Gagal mencatat riwayat Job %s: %v", record.JobID, err)
	} else {
		log.Printf("💾 [OMNI-DB] Jejak Job %s (%s) → Firestore ✅", record.JobID, record.Status)
	}
}

// RecordJobStart mencatat bahwa sebuah job baru saja dimulai
func RecordJobStart(jobID, toolID, inputFile string, inputSize int64) {
	RecordJobHistory(JobRecord{
		JobID:     jobID,
		ToolID:    toolID,
		Status:    "PROCESSING",
		InputFile: inputFile,
		InputSize: inputSize,
		CreatedAt: time.Now().Unix(),
	})
}

// RecordJobDone mencatat bahwa sebuah job telah selesai sukses
func RecordJobDone(jobID, outputFile string) {
	if OmniDB == nil {
		return
	}

	update := map[string]interface{}{
		"status":      "COMPLETED",
		"output_file": outputFile,
		"finished_at": time.Now().Unix(),
	}

	_, err := OmniDB.Collection("OmniJobs").Doc(jobID).Set(FireCtx, update, firestore.MergeAll)
	if err != nil {
		log.Printf("⚠️ [OMNI-DB] Gagal update status Job %s: %v", jobID, err)
	} else {
		log.Printf("💾 [OMNI-DB] Job %s → COMPLETED ✅", jobID)
	}
}

// RecordJobFailed mencatat bahwa sebuah job gagal
func RecordJobFailed(jobID, errMsg string) {
	if OmniDB == nil {
		return
	}

	update := map[string]interface{}{
		"status":      "FAILED",
		"error":       errMsg,
		"finished_at": time.Now().Unix(),
	}

	_, err := OmniDB.Collection("OmniJobs").Doc(jobID).Set(FireCtx, update, firestore.MergeAll)
	if err != nil {
		log.Printf("⚠️ [OMNI-DB] Gagal update status Job %s: %v", jobID, err)
	} else {
		log.Printf("💾 [OMNI-DB] Job %s → FAILED ❌", jobID)
	}
}

// ==========================================
// 🔑 API KEY VALIDATION
// ==========================================

// IsApiKeyValid mengecek apakah string Kunci API terdaftar di Koleksi "ApiKeys"
func IsApiKeyValid(key string) bool {
	if OmniDB == nil {
		log.Println("⚠️ [OMNI-DB] Firebase mati! Melewatkan cek API Key (Mode Fallback).")
		// Jika kita ingin strict mode, kembalikan false.
		// Jika ingin dev mode tanpa rintangan, kembalikan true.
		// Untuk Production, KEMBALIKAN FALSE.
		return false
	}

	doc, err := OmniDB.Collection("ApiKeys").Doc(key).Get(FireCtx)
	if err != nil {
		// Logika jika tidak ketemu atau error timeout
		return false
	}

	return doc.Exists()
}
