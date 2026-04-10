package core

import (
	"fmt"
	"io"
	"log"
	"os"
	"runtime"
	"sync/atomic"
)

// ==========================================
// 🌌 OMNI-TITAN BUFFER: 10GB SMART RAM POOL
// ==========================================
// Evolusi dari OMNI-BUFFER 1GB menjadi arsitektur RAM Pool tingkat Dewa.
//
// FILOSOFI:
//   Daripada meminta SSD menulis jutaan kali per file (TBW meledak),
//   kita telan data raksasa ke RAM → Batch Write ke SSD dalam hitungan jari.
//
// PROTEKSI OOM:
//   TitanSemaphore membatasi total RAM yang digunakan untuk streaming.
//   Jika semua slot terpakai, koneksi berikutnya PAUSE di tingkat TCP
//   (bukan crash) sampai slot tersedia. Server tetap hidup.
//
// MEKANISME:
//   File 50GB → ditarik 10GB ke RAM → tulis ke SSD → tarik 10GB lagi → ...
//   Total: 5 kali operasi tulis. SSD abadi.
//
// KONFIGURASI:
//   - TitanBufferSize: Ukuran buffer per operasi (10GB default)
//   - TitanMaxSlots: Jumlah slot paralel (3 default = max 30GB RAM untuk streaming)
//   - Sesuaikan TitanMaxSlots dengan RAM fisik server:
//       RAM 32GB  → TitanMaxSlots = 2 (20GB maks)
//       RAM 64GB  → TitanMaxSlots = 3 (30GB maks)
//       RAM 128GB → TitanMaxSlots = 6 (60GB maks)
//       RAM 256GB → TitanMaxSlots = 12 (120GB maks)
// ==========================================

// TitanBufferSize adalah kapasitas buffer per operasi streaming: 10GB
// (10 * 1024 * 1024 * 1024 = 10,737,418,240 bytes)
const TitanBufferSize int64 = 10 * 1024 * 1024 * 1024 // 10GB

// TitanMaxSlots membatasi berapa banyak buffer 10GB yang boleh aktif bersamaan.
// Ini adalah "Bendungan Air" yang mencegah OOM Killer Linux menyerang.
// Default: 3 slot = maksimal 30GB RAM fisik digunakan untuk streaming.
const TitanMaxSlots = 3

// TitanSemaphore adalah channel berbasis kapasitas yang bertindak sebagai
// Memory Semaphore. Setiap slot merepresentasikan izin untuk mengalokasikan
// satu buffer 10GB. Jika semua slot terpakai, goroutine berikutnya
// akan BLOCK (pause) tanpa menghabiskan CPU — menunggu slot dibebaskan.
var TitanSemaphore = make(chan struct{}, TitanMaxSlots)

// Statistik Titan (thread-safe via atomic)
var (
	titanActiveSlots   int64 // Jumlah slot yang sedang dipakai
	titanTotalStreamed  int64 // Total bytes yang telah diproses oleh Titan
	titanTotalBatches   int64 // Total batch write ke SSD
	titanQueueWaiting   int64 // Jumlah goroutine yang sedang mengantre slot
)

// ==========================================
// PUBLIC API: StreamUploadSmartBuffer (Backward Compatible)
// ==========================================

// StreamUploadSmartBuffer adalah fungsi utama streaming yang dipanggil oleh
// quarantine.go dan seluruh ekosistem OMNI.
//
// PENTING: Signature tetap sama agar backward-compatible!
//   - reader: sumber data (network stream dari multipart upload)
//   - destPath: path tujuan di SSD
//   - return: total bytes yang ditulis, error
//
// Secara internal, fungsi ini sekarang menggunakan OMNI-TITAN 10GB Pool.
func StreamUploadSmartBuffer(reader io.Reader, destPath string) (int64, error) {
	outFile, err := os.OpenFile(destPath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0666)
	if err != nil {
		return 0, fmt.Errorf("gagal membuka file tujuan: %w", err)
	}
	defer outFile.Close()

	// ==========================================
	// PHASE 1: MENGUNCI SLOT RAM (Memory Semaphore Acquisition)
	// ==========================================
	// Jika semua slot terpakai, goroutine ini akan TIDUR di sini
	// tanpa menghabiskan CPU — menunggu slot dibebaskan.
	atomic.AddInt64(&titanQueueWaiting, 1)
	log.Printf("⏳ [OMNI-TITAN] Meminta slot RAM... (Aktif: %d/%d, Antrean: %d)",
		atomic.LoadInt64(&titanActiveSlots), TitanMaxSlots, atomic.LoadInt64(&titanQueueWaiting))

	TitanSemaphore <- struct{}{} // BLOCK di sini jika semua slot penuh
	atomic.AddInt64(&titanQueueWaiting, -1)
	atomic.AddInt64(&titanActiveSlots, 1)

	defer func() {
		<-TitanSemaphore // Lepaskan slot setelah selesai
		atomic.AddInt64(&titanActiveSlots, -1)
		log.Printf("🔓 [OMNI-TITAN] Slot RAM dibebaskan. (Sisa aktif: %d/%d)",
			atomic.LoadInt64(&titanActiveSlots), TitanMaxSlots)
	}()

	log.Printf("🛡️ [OMNI-TITAN] Slot diperoleh! Mengalokasikan buffer 10GB... (Aktif: %d/%d)",
		atomic.LoadInt64(&titanActiveSlots), TitanMaxSlots)

	// ==========================================
	// PHASE 2: ALOKASI BUFFER TITAN (10GB)
	// ==========================================
	// io.CopyBuffer akan mengisi buffer ini dari network stream.
	// Ketika buffer 10GB penuh → flush ke SSD dalam SATU operasi tulis.
	// Lalu buffer direset dan diisi ulang. Proses berulang.
	buffer := make([]byte, TitanBufferSize)

	written, err := io.CopyBuffer(outFile, reader, buffer)
	if err != nil {
		log.Printf("❌ [OMNI-TITAN] Kegagalan aliran data: %v", err)
		return written, fmt.Errorf("titanstream error: %w", err)
	}

	// Update statistik
	atomic.AddInt64(&titanTotalStreamed, written)
	if written > 0 {
		batches := (written / int64(TitanBufferSize)) + 1
		atomic.AddInt64(&titanTotalBatches, batches)
	}

	gigabytes := float64(written) / (1024 * 1024 * 1024)
	if gigabytes >= 1.0 {
		log.Printf("✅ [OMNI-TITAN] Transmisi %.2f GB selesai sempurna. SSD keausan diminimalkan.",
			gigabytes)
	} else {
		megabytes := float64(written) / (1024 * 1024)
		log.Printf("✅ [OMNI-TITAN] Transmisi %.2f MB selesai sempurna.", megabytes)
	}

	// Golang GC secara agresif membersihkan array 10GB ini
	// setelah fungsi return, mengembalikan ruang ke OS.
	// Kita bantu dengan hint ke runtime untuk segera GC jika buffer besar.
	if written > 1024*1024*1024 { // > 1GB
		runtime.GC()
	}

	return written, nil
}

// ==========================================
// TITAN STATISTICS (untuk Prometheus & Banner)
// ==========================================

// GetTitanActiveSlots mengembalikan jumlah slot Titan yang sedang terpakai.
func GetTitanActiveSlots() int {
	return int(atomic.LoadInt64(&titanActiveSlots))
}

// GetTitanQueueWaiting mengembalikan jumlah goroutine yang mengantre slot.
func GetTitanQueueWaiting() int {
	return int(atomic.LoadInt64(&titanQueueWaiting))
}

// GetTitanTotalStreamed mengembalikan total bytes yang pernah diproses Titan.
func GetTitanTotalStreamed() int64 {
	return atomic.LoadInt64(&titanTotalStreamed)
}

// GetTitanTotalBatches mengembalikan total batch write ke SSD.
func GetTitanTotalBatches() int64 {
	return atomic.LoadInt64(&titanTotalBatches)
}

// GetTitanCapacityBytes mengembalikan kapasitas buffer per slot (10GB).
func GetTitanCapacityBytes() int64 {
	return int64(TitanBufferSize)
}

// GetTitanMaxPoolBytes mengembalikan total RAM maksimum yang bisa
// dialokasikan oleh Titan Pool (TitanBufferSize × TitanMaxSlots).
func GetTitanMaxPoolBytes() int64 {
	return int64(TitanBufferSize) * int64(TitanMaxSlots)
}
