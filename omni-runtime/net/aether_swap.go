package net

import (
	"context"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"sync"
	"time"
)

// ==========================================
// ⏳ OMNI-AETHER: ZERO-DOWNTIME HOT-SWAP
// ==========================================
// Pemusnahan proses deploy tradisional (502 Bad Gateway).
//
// ARSITEKTUR (Mitosis Biner):
//   1. Developer mengetik: omni deploy --hot
//   2. Biner lama mendeteksi sinyal OS (SIGHUP/Interrupt)
//   3. Biner lama mengekstrak TCP File Descriptor yang sedang aktif
//   4. Biner lama melahirkan biner BARU dan mewariskan FD TCP
//   5. Biner baru langsung menerima koneksi BARU
//   6. Biner lama menunggu koneksi lama selesai, lalu mati perlahan
//   7. Pengguna: TIDAK MERASAKAN APA-APA. Zero downtime!
//
// KEUNGGULAN vs Kubernetes Rolling Update:
//   K8s: Butuh pod baru, health check, drain period, 502 saat transisi
//   AETHER: FD inheritance langsung, zero packet loss, instant swap
//
// CROSS-PLATFORM:
//   Windows: os.Interrupt (CTRL+C / signal dari luar)
//   Linux:   SIGHUP + SIGUSR2 (via aether_swap_unix.go build tag)
// ==========================================

// AetherSwapper mengelola proses hot-swap
type AetherSwapper struct {
	server     *http.Server
	listener   net.Listener
	isChild    bool // Apakah proses ini adalah child dari hot-swap?
	mu         sync.Mutex
	swapping   bool
	generation int // Generasi biner (naik setiap hot-swap)
}

// NewAetherSwapper membuat instance hot-swapper
func NewAetherSwapper(server *http.Server, generation int) *AetherSwapper {
	return &AetherSwapper{
		server:     server,
		generation: generation,
	}
}

// ListenAndServeGraceful menjalankan server dengan dukungan hot-swap.
// Jika flag -graceful-restart ada, server mewarisi FD dari parent.
func (a *AetherSwapper) ListenAndServeGraceful(addr string, isGraceful bool) error {
	var ln net.Listener
	var err error

	if isGraceful {
		// CHILD MODE: Warisi File Descriptor dari parent!
		log.Println("🔄 [OMNI-AETHER] Mode Graceful Restart — mewarisi TCP socket dari parent...")

		// FD 3 = pertama ExtraFiles (0=stdin, 1=stdout, 2=stderr, 3=first extra)
		file := os.NewFile(3, "inherited-tcp")
		if file == nil {
			return fmt.Errorf("gagal mewarisi FD dari parent")
		}
		defer file.Close()

		ln, err = net.FileListener(file)
		if err != nil {
			return fmt.Errorf("gagal membuat listener dari inherited FD: %w", err)
		}
		a.isChild = true
		a.generation++

		log.Printf("✅ [OMNI-AETHER] Generasi #%d — Socket TCP berhasil diwarisi! Zero downtime!", a.generation)
	} else {
		// NORMAL MODE: Buat listener baru
		ln, err = net.Listen("tcp", addr)
		if err != nil {
			return fmt.Errorf("gagal listen di %s: %w", addr, err)
		}
		log.Printf("🌍 [OMNI-AETHER] Generasi #%d — Listening di %s", a.generation, addr)
	}

	a.listener = ln

	// Pasang signal handler untuk hot-swap
	go a.watchForSwapSignal()

	// Serve!
	a.server.Serve(ln)
	return nil
}

// watchForSwapSignal menunggu sinyal OS untuk trigger hot-swap atau shutdown.
// Menggunakan os.Interrupt yang didukung semua platform (Windows, Linux, Mac).
func (a *AetherSwapper) watchForSwapSignal() {
	sigChan := make(chan os.Signal, 1)

	// os.Interrupt = CTRL+C (didukung SEMUA OS termasuk Windows)
	// Untuk hot-swap di Linux/Mac, kirim: kill -HUP <pid>
	// Di Windows: gunakan omni deploy --hot yang mengirim sinyal via API
	signal.Notify(sigChan, os.Interrupt)

	// Juga daftarkan sinyal platform-specific via fungsi terpisah
	registerPlatformSignals(sigChan)

	for sig := range sigChan {
		log.Printf("📡 [OMNI-AETHER] Sinyal diterima: %v", sig)

		// Cek apakah sinyal ini adalah trigger hot-swap
		if isHotSwapSignal(sig) {
			log.Println("🔄 [OMNI-AETHER] Hot-swap signal — Memulai Protokol Mitosis!")
			if err := a.TriggerHotSwap(); err != nil {
				log.Printf("💥 [OMNI-AETHER] Hot-swap gagal: %v", err)
			}
		} else {
			// SIGINT/SIGTERM → graceful shutdown
			log.Println("🛑 [OMNI-AETHER] Shutdown signal — Graceful shutdown...")
			a.GracefulShutdown()
			return
		}
	}
}

// TriggerHotSwap memulai proses mitosis: spawn biner baru + transfer FD
func (a *AetherSwapper) TriggerHotSwap() error {
	a.mu.Lock()
	if a.swapping {
		a.mu.Unlock()
		return fmt.Errorf("hot-swap sudah berjalan")
	}
	a.swapping = true
	a.mu.Unlock()

	defer func() {
		a.mu.Lock()
		a.swapping = false
		a.mu.Unlock()
	}()

	log.Println("🔄 [OMNI-AETHER] Mengekstrak TCP File Descriptor...")

	// Ekstrak FD dari listener yang sedang aktif
	tcpLn, ok := a.listener.(*net.TCPListener)
	if !ok {
		return fmt.Errorf("listener bukan TCPListener")
	}

	file, err := tcpLn.File()
	if err != nil {
		return fmt.Errorf("gagal mengekstrak FD: %w", err)
	}
	defer file.Close()

	// Spawn biner baru dengan flag graceful-restart
	cmd := exec.Command(os.Args[0])
	cmd.Args = append(os.Args, "-graceful-restart")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.ExtraFiles = []*os.File{file} // ⚡ FD diwariskan ke child!
	cmd.Env = append(os.Environ(), fmt.Sprintf("OMNI_GENERATION=%d", a.generation+1))

	if err := cmd.Start(); err != nil {
		return fmt.Errorf("gagal spawn child process: %w", err)
	}

	log.Printf("✅ [OMNI-AETHER] Child process (PID %d) telah lahir dengan FD aktif!", cmd.Process.Pid)
	log.Println("⏳ [OMNI-AETHER] Parent akan mati setelah semua request lama selesai...")

	// Parent: graceful shutdown (tunggu request lama selesai)
	a.GracefulShutdown()

	return nil
}

// GracefulShutdown menunggu semua koneksi aktif selesai, lalu mati
func (a *AetherSwapper) GracefulShutdown() {
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	log.Println("⏳ [OMNI-AETHER] Menunggu koneksi aktif selesai (max 60 detik)...")

	if err := a.server.Shutdown(ctx); err != nil {
		log.Printf("⚠️ [OMNI-AETHER] Shutdown timeout, force close: %v", err)
	}

	log.Printf("🪦 [OMNI-AETHER] Generasi #%d — Rest In Peace. Penerus telah mengambil alih.", a.generation)
}
