package services

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"time"

	"omnitools/core"
)

// Struktur Data Template CLI
type CLITemplate struct {
	Binary      string   `json:"binary"`
	Args        []string `json:"args"`
	TimeoutMins int      `json:"timeout_mins"`
}

var cliRegistry map[string]CLITemplate

// Muat registry saat server menyala (Panggil di main.go)
func LoadCLIRegistry() {
	file, err := os.ReadFile(core.ResolveConfigPath("cli_registry.json"))
	if err != nil {
		WriteLog("SYSTEM", "WARN_CLI", "Tidak dapat membaca cli_registry.json, mengabaikan muat config.")
		return
	}

	var rawData map[string]json.RawMessage
	if err := json.Unmarshal(file, &rawData); err != nil {
		WriteLog("SYSTEM", "ERR_CLI_PARSE", fmt.Sprintf("Gagal parse root cli_registry.json: %v", err))
		return
	}

	rawToolsMsg, ok := rawData["tools"]
	if !ok {
		WriteLog("SYSTEM", "ERR_CLI_PARSE", "Kunci 'tools' tidak ditemukan di cli_registry.json")
		return
	}

	var rawTools map[string]json.RawMessage
	if err := json.Unmarshal(rawToolsMsg, &rawTools); err != nil {
		WriteLog("SYSTEM", "ERR_CLI_PARSE", fmt.Sprintf("Gagal parse tools cli_registry.json: %v", err))
		return
	}

	cliRegistry = make(map[string]CLITemplate)

	for key, rawMsg := range rawTools {
		// Abaikan elemen dokumentasi / kategori yang diawali dengan "=" atau "_"
		if strings.HasPrefix(key, "=") || strings.HasPrefix(key, "_") {
			continue
		}

		var tmpl CLITemplate
		if err := json.Unmarshal(rawMsg, &tmpl); err != nil {
			WriteLog("SYSTEM", "WARN_CLI_PARSE", fmt.Sprintf("Gagal parse template untuk '%s': %v", key, err))
			continue
		}
		cliRegistry[key] = tmpl
	}

	WriteLog("SYSTEM", "INFO_CLI", fmt.Sprintf("Berhasil memuat %d CLI Templates.", len(cliRegistry)))
}

// Fungsi utama untuk merakit dan mengeksekusi alat
func ExecuteUniversalTool(toolID string, inputPath string, outputPath string, outputDir string, dynamicParams map[string]string) ([]byte, error) {
	// 1. CEK KEBERADAAN (Safety Guard)
	template, exists := cliRegistry[toolID]
	if !exists {
		// Jika Anda salah ketik ID di Frontend, Golang akan menangkapnya di sini
		return nil, fmt.Errorf("TOOL_NOT_FOUND: ID '%s' tidak terdaftar di registry", toolID)
	}

	// 1.5. THE SCOUT (Pre-flight Validation)
	// Jika klien iseng mengirim log.txt yang direname jadi video.mp4, FFprobe akan langsung cegat!
	if err := ValidateMediaPreFlight(toolID, inputPath); err != nil {
		return nil, err
	}

	// 2. PROSES ARGUMEN (Tanpa Error Manual)
	var finalArgs []string
	for _, arg := range template.Args {
		processedArg := strings.ReplaceAll(arg, "{input}", inputPath)
		processedArg = strings.ReplaceAll(processedArg, "{output}", outputPath)
		processedArg = strings.ReplaceAll(processedArg, "{output_dir}", outputDir)

		// Loop aman untuk parameter dinamis
		for key, val := range dynamicParams {
			processedArg = strings.ReplaceAll(processedArg, "{"+key+"}", val)
		}
		finalArgs = append(finalArgs, processedArg)
	}

	// 2. THE OPTIMIZER (Langkah Cerdas): Auto-Tune Bitrate Video sebelum diproses!
	finalArgs = AutoTuneVideo(toolID, inputPath, finalArgs)

	WriteLog("CLI_EXECUTOR", "INFO", fmt.Sprintf("Template Dirakit setelah Optimus: %s %v", template.Binary, finalArgs))

	// 3. Eksekusi menggunakan Pabrik Pekerja Multi-Lajur (The Fair Manager)
	timeout := time.Duration(template.TimeoutMins) * time.Minute
	if template.TimeoutMins <= 0 {
		timeout = 5 * time.Minute // default
	}

	// Submit dengan Pabrik Pekerja (Suntikkan Alchemist Biner)
	alchemistEngine := ResolveBinary(template.Binary)
	result := SubmitJobWithTimeout(toolID, alchemistEngine, finalArgs, timeout)

	if !result.Success {
		WriteLog("CLI_EXECUTOR", "ERROR", fmt.Sprintf("Gagal mengeksekusi %s (%s): %v", toolID, alchemistEngine, result.Error))
		return nil, result.Error
	}

	return result.Data, nil
}
