package services

import (
	"log"
	"path/filepath"

	"github.com/glebarez/sqlite"
	"gorm.io/gorm"
)

// ==========================================
// 🗄️ OMNI-ORACLE: DATABASE SCHEMA HEALER
// ==========================================

// Global DB Instance
var DB *gorm.DB

// ToolLog represents a history of tool executions for auditing and AI learning
type ToolLog struct {
	gorm.Model
	ToolID    string `gorm:"index"`
	Operation string
	Status    string // success, error, processing
	ErrorMsg  string
	Duration  int64  // in milliseconds
	Metadata  string `gorm:"type:text"` // JSON metadata
}

// SystemConfig represents persistent OMNI settings
type SystemConfig struct {
	Key   string `gorm:"primaryKey"`
	Value string
}

func InitDBAutoHeal() {
	log.Println("🔍 [OMNI-ORACLE] Menganalisis Schema Database (Drift Detection)...")

	// Gunakan SQLite di folder release/omni_cache agar portable & local-first
	dbPath := filepath.Join("..", "release", "omni_cache", "omni_oracle.db")

	db, err := gorm.Open(sqlite.Open(dbPath), &gorm.Config{})
	if err != nil {
		log.Fatalf("❌ [DB FATAL] Gagal terhubung ke Database: %v", err)
	}

	// 🛠️ AUTO-HEAL: GORM secara otomatis menyinkronkan Struct dengan Tabel SQL.
	// Jika Anda menambah field di struct di atas, GORM akan melakukan ALTER TABLE otomatis.
	err = db.AutoMigrate(&ToolLog{}, &SystemConfig{})
	if err != nil {
		log.Fatalf("❌ [DB HEAL FATAL] Gagal memperbaiki struktur tabel: %v", err)
	}

	DB = db
	log.Println("✅ [DB SYNC] Logika Struct dan Database SQLite 100% Identik.")
}
