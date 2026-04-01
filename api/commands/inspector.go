package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"strings"
	"time"
)

// Struktur Registry Mirip dengan yang ada di services
type CLITemplate struct {
	Binary      string   `json:"binary"`
	Args        []string `json:"args"`
	TimeoutMins int      `json:"timeout_mins"`
}

type CLIRegistry struct {
	Tools map[string]json.RawMessage `json:"tools"`
}

func main() {
	fmt.Println("=========================================")
	fmt.Println("🕵️  THE INSPECTOR: PROTOKOL SANITY CHECK")
	fmt.Println("=========================================")

	registryPath := "../configs/cli_registry.json"
	data, err := ioutil.ReadFile(registryPath)
	if err != nil {
		fmt.Printf("❌ [FATAL] Tidak bisa membaca file registry: %v\n", err)
		os.Exit(1)
	}

	var registry CLIRegistry
	if err := json.Unmarshal(data, &registry); err != nil {
		fmt.Printf("❌ [FATAL] Syntax Error pada JSON registry: %v\n", err)
		os.Exit(1)
	}

	totalTools := 0
	passCount := 0
	failCount := 0

	fmt.Println("🔍 Memulai Inspeksi Pustaka Alat...")
	time.Sleep(500 * time.Millisecond)

	for id, raw := range registry.Tools {
		// Abaikan komentar pada JSON
		if strings.HasPrefix(id, "_") || strings.HasPrefix(id, "=") {
			continue
		}

		var template CLITemplate
		if err := json.Unmarshal(raw, &template); err != nil {
			fmt.Printf("❌ [%s] GAGAL PARSING KONFIGURASI: %v\n", id, err)
			failCount++
			continue
		}

		totalTools++

		// 1. Cek Komponen
		if template.Binary == "" || len(template.Args) == 0 {
			fmt.Printf("❌ [%s] GAGAL: Binary atau Argrumen kosong.\n", id)
			failCount++
			continue
		}

		// 2. Lacak Binary di Path OS Host
		_, err := exec.LookPath(template.Binary)
		if err != nil {
			fmt.Printf("⚠️  [%s] PERINGATAN: Binary '%s' belum ter-install di OS ini.\n", id, template.Binary)
			// Tetap hitung pass jika ini sekadar dev PC, karena nanti di Docker akan ada.
			// Tetapi beri peringatan ekstrim.
		}

		// 3. Verifikasi Logika Param {input} & {output}
		hasInput := false
		hasOutput := false
		for _, arg := range template.Args {
			if strings.Contains(arg, "{input}") {
				hasInput = true
			}
			if strings.Contains(arg, "{output}") || strings.Contains(arg, "{output_dir}") {
				hasOutput = true
			}
		}

		if !hasInput {
			fmt.Printf("❌ [%s] CRITICAL: Parameter {input} tidak ditemukan!\n", id)
			failCount++
			continue
		}
		if !hasOutput {
			fmt.Printf("❌ [%s] CRITICAL: Parameter {output}/{output_dir} tidak ditemukan!\n", id)
			failCount++
			continue
		}

		// Jika lolos semua cek logis The Inspector
		passCount++
	}

	fmt.Println("\n=========================================")
	fmt.Println("📊 LAPORAN THE INSPECTOR")
	fmt.Println("=========================================")
	fmt.Printf("🛠️  Total Alat  : %d\n", totalTools)
	fmt.Printf("✅ Siap Tempur: %d\n", passCount)
	fmt.Printf("❌ Cacat      : %d\n", failCount)
	fmt.Println("=========================================")

	if failCount > 0 {
		fmt.Println("🚨 SISTEM TIDAK STABIL! MOHON PERBAIKI ERROR SEBELUM NAIK KE PRODUKSI.")
		os.Exit(1)
	} else {
		fmt.Println("🟢 FRAMEWORK OMNI TOOLS 100% AMAN DAN SIAP PERANG!")
	}
}
