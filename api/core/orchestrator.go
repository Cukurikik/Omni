package core

import (
	"fmt"
	"time"
)

// JobResult adalah hasil dari eksekusi tool.
type JobResult struct {
	Success bool
	Data    []byte
	Error   error
}

// Job merepresentasikan satu unit pekerjaan yang diproses oleh antrean.
type Job struct {
	ID        string
	Category  string // "FAST", "MEDIUM", atau "HEAVY"
	EngineCmd string
	Args      []string
	Timeout   time.Duration
	Result    chan JobResult
}

// JobExecutor adalah tipe fungsi yang akan disuntikkan (Dependency Injection)
// Ini memungkinkan Orchestrator memanggil logika Engine tanpa Circular Import.
type JobExecutor func(job *Job) ([]byte, error)

// GlobalExecutor adalah variabel global tempat Engine mendaftarkan dirinya.
var GlobalExecutor JobExecutor

// ExecuteTool adalah gerbang utama eksekusi tool.
func ExecuteTool(job *Job) ([]byte, error) {
	if GlobalExecutor == nil {
		return nil, fmt.Errorf("engine executor belum terdaftar (GlobalExecutor is nil)")
	}
	return GlobalExecutor(job)
}
