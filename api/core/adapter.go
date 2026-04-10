package core

import (
	"fmt"
	"log"
	"sync"
	"time"
)

// ==========================================
// 🔌 OMNI-ADAPTER: SECURE THIRD-PARTY INTEGRATION
// ==========================================
// Membungkus SEMUA integrasi pihak ketiga (Stripe, SendGrid, Twilio,
// OpenAI, dsb.) dalam lapisan pelindung "Quarantine Adapter".
//
// Filosofi: Buka pintunya, tapi pasang Penjaga Gerbang Paling Kejam.
//   - Setiap adapter di-register dengan health check
//   - Jika satu adapter gagal → OMNI TETAP HIDUP (graceful degradation)
//   - Status semua adapter bisa dipantau real-time via /api/v1/adapters/status
//   - Circuit breaker: jika gagal 3x berturut → adapter auto-disable selama 60 detik
//
// Developer cukup:
//   1. RegisterAdapter("stripe", stripeHealthCheck)
//   2. core.Adapter("stripe").Call(func() error { ... })
//
// OMNI akan menangani retry, circuit breaking, dan logging secara otomatis.
// ==========================================

// AdapterState merepresentasikan status hidup/mati sebuah adapter
type AdapterState string

const (
	AdapterActive   AdapterState = "ACTIVE"
	AdapterDegraded AdapterState = "DEGRADED"
	AdapterDead     AdapterState = "DEAD"
	AdapterCooldown AdapterState = "COOLDOWN"
)

// AdapterEntry adalah metadata satu integrasi pihak ketiga
type AdapterEntry struct {
	Name          string       `json:"name"`
	State         AdapterState `json:"state"`
	FailCount     int          `json:"fail_count"`
	LastChecked   time.Time    `json:"last_checked"`
	LastError     string       `json:"last_error,omitempty"`
	CooldownUntil time.Time    `json:"cooldown_until,omitempty"`
	healthCheck   func() error // internal: fungsi untuk mengecek kesehatan
	mu            sync.Mutex
}

// adapterRegistry menyimpan SEMUA adapter yang terdaftar
type adapterRegistry struct {
	mu       sync.RWMutex
	adapters map[string]*AdapterEntry
}

var registry = &adapterRegistry{
	adapters: make(map[string]*AdapterEntry),
}

const (
	maxFailBeforeCooldown = 3              // 3x gagal berturut → cooldown
	cooldownDuration      = 60 * time.Second // cooldown 60 detik
)

// ==========================================
// PUBLIC API: Registrasi & Pemanggilan
// ==========================================

// RegisterAdapter mendaftarkan integrasi pihak ketiga ke OMNI.
// healthCheck adalah fungsi yang memverifikasi apakah service third-party siap.
//
// Contoh:
//
//	core.RegisterAdapter("stripe", func() error {
//	    resp, err := http.Get("https://api.stripe.com/v1/health")
//	    if err != nil || resp.StatusCode != 200 { return fmt.Errorf("stripe down") }
//	    return nil
//	})
func RegisterAdapter(name string, healthCheck func() error) {
	registry.mu.Lock()
	defer registry.mu.Unlock()

	registry.adapters[name] = &AdapterEntry{
		Name:        name,
		State:       AdapterActive,
		healthCheck: healthCheck,
		LastChecked: time.Now(),
	}
	log.Printf("🔌 [OMNI-ADAPTER] Adapter '%s' terdaftar. Status: ACTIVE", name)
}

// Adapter mengambil entry adapter berdasarkan nama.
// Mengembalikan nil jika adapter tidak terdaftar.
func Adapter(name string) *AdapterEntry {
	registry.mu.RLock()
	defer registry.mu.RUnlock()
	return registry.adapters[name]
}

// Call mengeksekusi fungsi dalam perlindungan adapter circuit breaker.
// Jika adapter sedang cooldown, panggilan ditolak tanpa mengeksekusi fn.
// Jika fn gagal, fail counter bertambah. Jika sudah 3x gagal berturut,
// adapter masuk cooldown 60 detik.
//
// Contoh:
//
//	err := core.Adapter("stripe").Call(func() error {
//	    return stripe.ChargeCustomer(...)
//	})
func (a *AdapterEntry) Call(fn func() error) error {
	if a == nil {
		return fmt.Errorf("[OMNI-ADAPTER] adapter tidak terdaftar")
	}

	a.mu.Lock()
	defer a.mu.Unlock()

	// Cek cooldown
	if a.State == AdapterCooldown {
		if time.Now().Before(a.CooldownUntil) {
			return fmt.Errorf("[OMNI-ADAPTER] '%s' dalam COOLDOWN hingga %s. Coba lagi nanti",
				a.Name, a.CooldownUntil.Format("15:04:05"))
		}
		// Cooldown selesai → kembalikan ke active
		a.State = AdapterActive
		a.FailCount = 0
		log.Printf("🔌 [OMNI-ADAPTER] '%s' telah bangun dari COOLDOWN. Status: ACTIVE", a.Name)
	}

	if a.State == AdapterDead {
		return fmt.Errorf("[OMNI-ADAPTER] '%s' dinyatakan MATI. Register ulang untuk menghidupkan", a.Name)
	}

	// Eksekusi fungsi yang sesungguhnya
	err := fn()
	a.LastChecked = time.Now()

	if err != nil {
		a.FailCount++
		a.LastError = err.Error()
		log.Printf("⚠️ [OMNI-ADAPTER] '%s' GAGAL (ke-%d): %v", a.Name, a.FailCount, err)

		if a.FailCount >= maxFailBeforeCooldown {
			a.State = AdapterCooldown
			a.CooldownUntil = time.Now().Add(cooldownDuration)
			log.Printf("🧊 [OMNI-ADAPTER] '%s' masuk COOLDOWN selama %s karena %dx gagal berturut!",
				a.Name, cooldownDuration, maxFailBeforeCooldown)
		} else {
			a.State = AdapterDegraded
		}
		return err
	}

	// Sukses — reset counter
	if a.FailCount > 0 {
		log.Printf("🔌 [OMNI-ADAPTER] '%s' telah pulih. Reset fail counter.", a.Name)
	}
	a.FailCount = 0
	a.State = AdapterActive
	a.LastError = ""
	return nil
}

// ==========================================
// HEALTH CHECK: Pengecekan Massal
// ==========================================

// AdapterStatus adalah laporan kesehatan satu adapter (untuk API response)
type AdapterStatus struct {
	Name        string       `json:"name"`
	State       AdapterState `json:"state"`
	FailCount   int          `json:"fail_count"`
	LastChecked string       `json:"last_checked"`
	LastError   string       `json:"last_error,omitempty"`
}

// CheckAllAdapters menjalankan health check pada SEMUA adapter dan mengembalikan laporan.
// Digunakan oleh endpoint /api/v1/adapters/status
func CheckAllAdapters() []AdapterStatus {
	registry.mu.RLock()
	adapters := make([]*AdapterEntry, 0, len(registry.adapters))
	for _, a := range registry.adapters {
		adapters = append(adapters, a)
	}
	registry.mu.RUnlock()

	results := make([]AdapterStatus, 0, len(adapters))

	for _, a := range adapters {
		a.mu.Lock()

		// Jalankan health check jika tersedia
		if a.healthCheck != nil && a.State != AdapterCooldown {
			if err := a.healthCheck(); err != nil {
				a.FailCount++
				a.LastError = err.Error()
				if a.FailCount >= maxFailBeforeCooldown {
					a.State = AdapterCooldown
					a.CooldownUntil = time.Now().Add(cooldownDuration)
				} else {
					a.State = AdapterDegraded
				}
			} else {
				a.State = AdapterActive
				a.FailCount = 0
				a.LastError = ""
			}
			a.LastChecked = time.Now()
		}

		results = append(results, AdapterStatus{
			Name:        a.Name,
			State:       a.State,
			FailCount:   a.FailCount,
			LastChecked: a.LastChecked.Format(time.RFC3339),
			LastError:   a.LastError,
		})

		a.mu.Unlock()
	}

	return results
}

// GetAdapterCount mengembalikan jumlah adapter yang terdaftar (untuk monitoring banner)
func GetAdapterCount() int {
	registry.mu.RLock()
	defer registry.mu.RUnlock()
	return len(registry.adapters)
}
