package core

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os/exec"
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

// CallUniversalWorker adalah jembatan penghubung antar dimensi bahasa
func CallUniversalWorker(job *Job, lang string, entryPoint string) ([]byte, error) {
	var cmd *exec.Cmd

	// Deteksi Runtime dan Siapkan Perintah
	switch lang {
	case "python":
		cmd = exec.Command("python3", entryPoint)
	case "nodejs":
		cmd = exec.Command("node", entryPoint)
	case "rust":
		cmd = exec.Command(entryPoint)
	default:
		// Jika Go, jalankan sebagai internal function (performa maksimal)
		return nil, fmt.Errorf("internal execution")
	}

	// JSON Payload untuk dikirim ke Worker (Python/Node/Rust)
	payload, _ := json.Marshal(job)
	cmd.Stdin = bytes.NewReader(payload)

	var out bytes.Buffer
	cmd.Stdout = &out

	err := cmd.Run()
	if err != nil {
		return nil, err
	}

	return out.Bytes(), nil
}
