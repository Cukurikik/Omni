package services

import (
	"fmt"
	"os/exec"
	"strings"
)

// ValidateMediaPreFlight bertindak sebagai "Pramuka".
// Ia menginspeksi jeroan file .mp4 / .mp3 sebelum dilempar ke Worker Pool.
// Jika file adalah dokumen teks yang di-rename menjadi .mp4, ffprobe akan langsung memblokirnya.
func ValidateMediaPreFlight(toolID string, filePath string) error {
	// Hanya inspeksi jika ada input file dan ini adalah kategori Media (Video/Audio)
	if filePath == "" {
		return nil
	}

	if !strings.HasPrefix(toolID, "video_") && !strings.HasPrefix(toolID, "audio_") {
		return nil
	}

	// Cek ketersediaan FFprobe di OS ini
	_, errPath := exec.LookPath("ffprobe")
	if errPath != nil {
		WriteLog("SCOUT", "WARN_NO_FFPROBE", "Binary 'ffprobe' tidak ditemukan di OS. Melompati tahap Pre-flight Validation.")
		return nil // Kita tidak memblokir server development jika belum terinstall ffmpeg
	}

	// Jalankan inspeksi membedah format & streams (Hanya membaca metadata, Nol-RAM bloat)
	cmd := exec.Command("ffprobe", "-v", "error", "-show_format", "-show_streams", filePath)
	output, err := cmd.CombinedOutput()
	if err != nil {
		WriteLog("SCOUT", "ERR_INVALID_MEDIA", fmt.Sprintf("File DITOLAK: '%s'. Isi file rusak/fake. Output: %s", filePath, string(output)))
		return fmt.Errorf("CORRUPT_MEDIA: Misi Dibatalkan! OMNI Scout mendeteksi file input adalah file media palsu atau rusak")
	}

	WriteLog("SCOUT", "PASS_MEDIA_CHECK", fmt.Sprintf("OMNI Scout mensertifikasi file aman diproses: %s", filePath))
	return nil
}
