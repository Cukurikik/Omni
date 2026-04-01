package services

import (
	"bufio"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"sync"
	"time"

	"omnitools/core"
)

// WalRecord adalah catatan yang diukir ke SSD
type WalRecord struct {
	JobID  string `json:"job_id"`
	Action string `json:"action"` // "ENQUEUE" atau "DEQUEUE"
	Data   *core.Job   `json:"data,omitempty"`
}

var (
	walMutex sync.Mutex
	walPath  = "../release/omni_queue.wal"
)

func getWalPath() string {
	if core.AppConfig != nil && core.AppConfig.Storage.QuarantineDir != "" {
		return filepath.Join(filepath.Dir(core.AppConfig.Storage.QuarantineDir), "logs", "omni_queue.wal")
	}
	// Fallback
	_ = os.MkdirAll("../release/logs", 0755)
	return "../release/logs/omni_queue.wal"
}

// WriteToWAL mengukir kejadian ke SSD sebelum diproses RAM
func WriteToWAL(action string, job *core.Job) {
	walMutex.Lock()
	defer walMutex.Unlock()

	path := getWalPath()

	// Pastikan folder tersedia
	_ = os.MkdirAll(filepath.Dir(path), 0755)

	// Buka file dengan mode APPEND (tambahkan di baris paling bawah)
	f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		WriteLog("AURA", "ERR_WAL_OPEN", fmt.Sprintf("Gagal membuka WAL: %v", err))
		return
	}
	defer f.Close()

	record := WalRecord{JobID: job.ID, Action: action, Data: job}
	jsonData, _ := json.Marshal(record)

	// Tulis ke SSD secepat kilat (Append-Only sangat ringan)
	f.WriteString(string(jsonData) + "\n")
}

// 🧟 PROTOKOL KEBANGKITAN

// RecoverLostJobs dipanggil SATU KALI saat server pertama kali booting
func RecoverLostJobs() []core.Job {
	walMutex.Lock()
	defer walMutex.Unlock()

	var lostJobs []core.Job
	activeJobs := make(map[string]core.Job)
	path := getWalPath()

	f, err := os.Open(path)
	if err != nil {
		if os.IsNotExist(err) {
			return lostJobs // Belum ada log, aman.
		}
		WriteLog("AURA", "ERR_WAL_READ", fmt.Sprintf("Gagal membaca WAL: %v", err))
		return lostJobs
	}
	defer f.Close()

	// Baca file baris per baris
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		var record WalRecord
		json.Unmarshal(scanner.Bytes(), &record)

		if record.Action == "ENQUEUE" && record.Data != nil {
			activeJobs[record.JobID] = *record.Data
		} else if record.Action == "DEQUEUE" {
			// Tugas sudah selesai sebelum mati lampu, hapus dari daftar
			delete(activeJobs, record.JobID)
		}
	}

	// Masukkan sisa tugas yang belum DEQUEUE ke array kebangkitan
	for _, job := range activeJobs {
		lostJobs = append(lostJobs, job)
	}

	return lostJobs
}

// RecoverAndRequeueLostJobs adalah orkestrator yang membangkitkan dan memasukkan
// kembali Job yang hilang di alam kematian langsung ke jalur antreannya
func RecoverAndRequeueLostJobs() {
	log.Println("🔍 [OMNI-AURA] Memindai file WAL untuk tugas yang terputus...")
	lostJobs := RecoverLostJobs()
	if len(lostJobs) > 0 {
		log.Printf("⚠️ [OMNI-AURA] Menemukan %d tugas yang terputus! Membangkitkan kembali...", len(lostJobs))

		// Set ulang file WAL agar tidak duplicate job (akan ditulis ulang otomatis oleh enqueue WAL baru jika ada)
		CompactWAL()

		for _, job := range lostJobs {
			// Perhatian: job.Result (channel) sudah hilang/nil. Worker harus siap mengeksekusi Job yang
			// tidak mem-block channel balasan karena klien aslinya sudah terputus.

			switch job.Category {
			case "FAST":
				// Re-Enqueue (background re-write WAL will be triggered locally inside worker if we bypass SubmitJobWithTimeout)
				// Tetapkan ulang channel nil (dulu interface, dibiarkan saja nil)
				// Dan kita langsung masukkan ke queue
				FastQueue <- job
				WriteLog("AURA", "INFO_RESURRECT", fmt.Sprintf("BANGKIT [FAST]: %s", job.ID))
			case "MEDIUM":
				MediumQueue <- job
				WriteLog("AURA", "INFO_RESURRECT", fmt.Sprintf("BANGKIT [MEDIUM]: %s", job.ID))
			case "HEAVY":
				HeavyQueue <- job
				WriteLog("AURA", "INFO_RESURRECT", fmt.Sprintf("BANGKIT [HEAVY]: %s", job.ID))
			default:
				log.Printf("❌ [OMNI-AURA] Job Korup tanpa Category: %s", job.ID)
			}
		}
	} else {
		log.Println("✅ [OMNI-AURA] Tidak ada tugas yang tertinggal. Sistem bersih.")
	}
}

// CompactWAL menghapus file log lama dan hanya menulis ulang tugas yang masih gantung
// (Mencegah file log membengkak jadi bergiga-giga)
func CompactWAL() {
	lostJobs := RecoverLostJobs()

	walMutex.Lock()
	defer walMutex.Unlock()

	path := getWalPath()
	os.Remove(path) // Hapus yang lama

	if len(lostJobs) > 0 {
		f, _ := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		defer f.Close()
		for _, job := range lostJobs {
			// Tulis ulang hanya yang belum selesai
			record := WalRecord{JobID: job.ID, Action: "ENQUEUE", Data: &job}
			jsonData, _ := json.Marshal(record)
			f.WriteString(string(jsonData) + "\n")
		}
	}
}

// StartWALCompactor membersihkan file log rutin setiap jam
func StartWALCompactor() {
	ticker := time.NewTicker(1 * time.Hour)
	defer ticker.Stop()

	for range ticker.C {
		CompactWAL()
	}
}
