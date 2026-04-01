package core

import (
	"encoding/json"
	"log"
	"os"
	"sync"
)

// OmniConfig menyimpan seluruh parameter vital framework
type OmniConfig struct {
	Port           string `json:"port"`
	MaxUploadGB    int64  `json:"max_upload_gb"`
	WorkerPoolSize int    `json:"worker_pool_size"`
	SessionSecret  string `json:"session_secret"`
	Env            string `json:"env"`         // "dev" atau "prod"
	FFmpegPath     string `json:"ffmpeg_path"` // Jalur absolut ke binary ffmpeg
}

var (
	Config *OmniConfig
	once   sync.Once
)

// LoadConfig dipanggil HANYA SEKALI saat server booting (Singleton)
func LoadConfig(path string) {
	once.Do(func() {
		file, err := os.ReadFile(path)
		if err != nil {
			log.Fatalf("❌ [CONFIG FATAL] Gagal membaca %s. Gunakan 'omni fix'. Detail error: %v", path, err)
		}

		Config = &OmniConfig{}
		if err := json.Unmarshal(file, Config); err != nil {
			log.Fatalf("❌ [CONFIG FATAL] Gagal unmarshal %s: %v", path, err)
		}
		log.Printf("⚙️ [OMNI CONFIG] Dimuat: Mode %s | Max Upload: %dGB", Config.Env, Config.MaxUploadGB)
		if Config.FFmpegPath != "" {
			log.Printf("⚙️ [OMNI CONFIG] FFmpeg Path: %s", Config.FFmpegPath)
		} else {
			log.Printf("⚠️ [OMNI CONFIG] FFmpeg Path TIDAK DITEMUKAN di omni_config.json")
		}
	})
}
