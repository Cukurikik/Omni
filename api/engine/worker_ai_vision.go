package engine

import (
	"log"
	"omnitools/core"
)

// ProcessAiVision adalah Jenderal Golang yang mengawasi Prajurit Python
func ProcessAiVision(job *core.Job) error {
	log.Printf("🤖 [AI-VISION] Menyerahkan tugas %s ke Python Engine...", job.ID)

	// ⚡ MEMANGGIL PYTHON VIA OMNI UNIVERSAL BRIDGE
	// Golang mengirim data Job (berisi InputPath & OutputPath) ke Python
	resultBytes, err := core.CallUniversalWorker(job, "python", "api/engine/ai_vision/main.py")

	if err != nil {
		log.Printf("❌ [AI-VISION] Prajurit Python Gagal Dieksekusi: %v", err)
		return err
	}

	// Python mencetak JSON hasil pekerjaannya, Golang membacanya.
	log.Printf("✅ [AI-VISION] Laporan Prajurit Python: %s", string(resultBytes))
	return nil
}
