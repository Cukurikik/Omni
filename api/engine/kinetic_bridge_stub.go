//go:build !cgo
// +build !cgo

package engine

import (
	"fmt"
	"log"
)

// ==========================================
// ⚡ OMNI-KINETIC: CGO STUB (Fallback)
// ==========================================
// File ini akan dikompilasi jika CGO dinonaktifkan (CGO_ENABLED=0).
// Ini mencegah compiler/IDE linter mengalami kepanikan (undefined functions)
// saat C compiler lokal tidak ditemukan.
// ==========================================

func KineticVersion() string {
	return "STUB_NO_CGO"
}

func KineticXorEncrypt(inputPath, outputPath string, xorKey byte) error {
	log.Printf("⚠️ [OMNI-KINETIC] CGO Disabled. Simulation mode for: %s", inputPath)
	return fmt.Errorf("KINETIC_ENGINE_DISABLED: Diperlukan kompilasi dengan CGO_ENABLED=1")
}

func KineticByteInvert(inputPath, outputPath string) error {
	log.Printf("⚠️ [OMNI-KINETIC] CGO Disabled. Simulation mode for: %s", inputPath)
	return fmt.Errorf("KINETIC_ENGINE_DISABLED: Diperlukan kompilasi dengan CGO_ENABLED=1")
}

func KineticChecksum(filePath string) (uint32, error) {
	log.Printf("⚠️ [OMNI-KINETIC] CGO Disabled. Simulation mode for: %s", filePath)
	return 0, fmt.Errorf("KINETIC_ENGINE_DISABLED: Diperlukan kompilasi dengan CGO_ENABLED=1")
}
