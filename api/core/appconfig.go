package core

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"sync"
)

// ==========================================
// 📖 THE OMNI READER: APPCONFIG MEMORY SINGLETON
// ==========================================
// Membaca configs/appconfig.json HANYA SATU KALI saat server boot,
// lalu menguncinya di RAM menggunakan sync.Once (Singleton Pattern).
//
// Akses dari mana saja: core.AppConfig.Server.Port
// Kecepatan akses: ~1 nanosecond (membaca variabel Go, bukan file disk)
// ==========================================

// AppConfigStruct memetakan seluruh isi appconfig.json secara presisi
type AppConfigStruct struct {
	AppName     string `json:"app_name"`
	Version     string `json:"version"`
	Environment string `json:"environment"`
	CliLanguage string `json:"cli_language"`

	Server struct {
		Host                    string `json:"host"`
		Port                    int    `json:"port"`
		ReadTimeoutSeconds      int    `json:"read_timeout_seconds"`
		WriteTimeoutSeconds     int    `json:"write_timeout_seconds"`
		GracefulShutdownSeconds int    `json:"graceful_shutdown_seconds"`
	} `json:"server"`

	Security struct {
		SessionSecret      string   `json:"session_secret"`
		CorsAllowedOrigins []string `json:"cors_allowed_origins"`
		RateLimitPerSecond int      `json:"rate_limit_per_second"`
		EnableCoopCoep     bool     `json:"enable_coop_coep"`
	} `json:"security"`

	Database struct {
		Engine string `json:"engine"` // postgres, firebase, or local
		URL    string `json:"url"`
	} `json:"database"`

	Storage struct {
		MaxUploadGB     int64  `json:"max_upload_gb"`
		QuarantineDir   string `json:"quarantine_dir"`
		CacheDir        string `json:"cache_dir"`
		CacheTTLMinutes int    `json:"cache_ttl_minutes"`
	} `json:"storage"`

	Engine struct {
		MaxConcurrentWorkers  int `json:"max_concurrent_workers"`
		GoWorkers             int `json:"go_workers"`
		FFmpegThrottleThreads int `json:"ffmpeg_throttle_threads"`
		JobCleanupHours       int `json:"job_cleanup_hours"`
	} `json:"engine"`

	Features struct {
		LiveReload bool `json:"live_reload"`
		Telemetry  bool `json:"telemetry"`
		AutoHeal   bool `json:"auto_heal"`
	} `json:"features"`

	Firebase struct {
		Enabled         bool   `json:"enabled"`
		CredentialsPath string `json:"credentials_path"`
		ProjectID       string `json:"project_id"`
	} `json:"firebase"`

	NexusCluster struct {
		Role                    string `json:"role"`                       // "master" atau "worker"
		MasterURL               string `json:"master_url"`                 // URL Master Node
		ClusterSecret           string `json:"cluster_secret"`             // Kunci autentikasi antar-node
		WorkerMaxJobs           int    `json:"worker_max_jobs"`            // Maks job paralel per worker
		HeartbeatIntervalSec    int    `json:"heartbeat_interval_seconds"` // Interval heartbeat (detik)
		DeadThresholdSec        int    `json:"dead_threshold_seconds"`     // Batas waktu node dianggap mati
	} `json:"nexus_cluster"`

	// V1.3: OMNI-CHAMELEON — CSS Framework & View Transitions
	UI struct {
		CSSFramework    string `json:"css_framework"`    // tailwind, bootstrap, bulma, none
		ViewTransitions bool   `json:"view_transitions"` // Enable View Transitions API
	} `json:"ui"`

	// V1.3: OMNI-WASM — WebAssembly Sandbox Configuration
	Wasm struct {
		Enabled       bool   `json:"enabled"`
		ModulesDir    string `json:"modules_dir"`
		MemoryLimitMB int    `json:"memory_limit_mb"` // Max RAM per Wasm module
	} `json:"wasm"`

	// V1.3: OMNI-UDS — Inter-Process Communication Configuration
	IPC struct {
		Mode       string `json:"mode"`        // uds, tcp, auto
		SocketPath string `json:"socket_path"` // Path untuk Unix Domain Socket
		Port       int    `json:"port"`        // Port untuk TCP fallback
	} `json:"ipc"`
}

var (
	// AppConfig adalah variabel global — bisa dipanggil dari seluruh file Go
	// Contoh: core.AppConfig.Storage.MaxUploadGB
	AppConfig     *AppConfigStruct
	appConfigOnce sync.Once
)

// LoadAppConfig membaca appconfig.json ke dalam memori (Singleton).
// Dipanggil SATU KALI di main.go saat server menyala.
//
// Parameter filepath menunjuk ke lokasi fisik file JSON:
//
//	core.LoadAppConfig("../configs/appconfig.json")
func LoadAppConfig(filepath string) {
	appConfigOnce.Do(func() {
		log.Println("📖 [OMNI READER] Membaca AppConfig ke dalam Memori Induk...")

		fileData, err := os.ReadFile(filepath)
		if err != nil {
			log.Fatalf("❌ [FATAL] Gagal membaca %s! Pastikan file ada atau jalankan 'omni fix'. Detail: %v", filepath, err)
		}

		AppConfig = &AppConfigStruct{}
		err = json.Unmarshal(fileData, AppConfig)
		if err != nil {
			log.Fatalf("❌ [FATAL] Format JSON %s rusak! Detail: %v", filepath, err)
		}

		// Default values untuk Nexus Cluster
		if AppConfig.NexusCluster.HeartbeatIntervalSec == 0 {
			AppConfig.NexusCluster.HeartbeatIntervalSec = 5
		}
		if AppConfig.NexusCluster.DeadThresholdSec == 0 {
			AppConfig.NexusCluster.DeadThresholdSec = 15
		}
		if AppConfig.NexusCluster.WorkerMaxJobs == 0 {
			AppConfig.NexusCluster.WorkerMaxJobs = 2
		}
		if AppConfig.NexusCluster.Role == "" {
			AppConfig.NexusCluster.Role = "master"
		}

		log.Printf("✅ [OMNI READER] Konfigurasi Dimuat:")
		log.Printf("   📛 Aplikasi       : %s v%s", AppConfig.AppName, AppConfig.Version)
		log.Printf("   🌍 Environment    : %s", AppConfig.Environment)
		log.Printf("   🚪 Server         : %s:%d", AppConfig.Server.Host, AppConfig.Server.Port)
		log.Printf("   📦 Max Upload     : %dGB", AppConfig.Storage.MaxUploadGB)
		log.Printf("   ⚙️  Workers        : %d C++/Py + %d Go", AppConfig.Engine.MaxConcurrentWorkers, AppConfig.Engine.GoWorkers)
		log.Printf("   🔧 FFmpeg Threads : %d", AppConfig.Engine.FFmpegThrottleThreads)
		if AppConfig.Firebase.Enabled {
			log.Printf("   🔥 Firebase       : AKTIF (Project: %s)", AppConfig.Firebase.ProjectID)
		} else {
			log.Printf("   🔥 Firebase       : NONAKTIF")
		}

		// Log Nexus Cluster status
		role := AppConfig.NexusCluster.Role
		if role == "master" {
			log.Printf("   👑 NEXUS Role     : MASTER (Armada Jenderal)")
		} else if role == "worker" {
			log.Printf("   🪖 NEXUS Role     : WORKER (Prajurit → %s)", AppConfig.NexusCluster.MasterURL)
		} else {
			log.Printf("   ⚪ NEXUS Role     : STANDALONE (Tidak dalam cluster)")
		}
	})
}

// GetServerAddr mengembalikan alamat server siap pakai (host:port)
func GetServerAddr() string {
	if AppConfig == nil {
		return "0.0.0.0:3000" // Fallback default
	}
	return fmt.Sprintf("%s:%d", AppConfig.Server.Host, AppConfig.Server.Port)
}

// IsProduction mengecek apakah server berjalan di mode produksi
func IsProduction() bool {
	if AppConfig == nil {
		return false
	}
	return AppConfig.Environment == "production"
}
