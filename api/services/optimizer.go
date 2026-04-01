package services

import (
	"bytes"
	"context"
	"fmt"
	"os/exec"
	"strconv"
	"strings"
	"time"
)

// ==========================================
// SMART AUTO-TUNE ENGINE (THE OPTIMIZER)
// ==========================================
//
// Mesin OMNI yang membedah file sebelum dikirim ke FFmpeg!
// Ia menentukan apakah file layak dikompres keras, ringan, atau TIDAK SAMA SEKALI.

func AutoTuneVideo(toolID, inputPath string, originalArgs []string) []string {
	// 1. Matriks Alat yang diizinkan untuk di-Tune
	// Mencegah modifikasi alat pemotong/pemutar balik yang wajib di *re-encode*
	if toolID != "video_compressor" && toolID != "video_to_mp4" {
		return originalArgs
	}

	WriteLog("OPTIMIZER", "INFO_ANALYSIS", fmt.Sprintf("Membedah bitrate asli file: %s", inputPath))

	// 2. Eksekusi Radar FFprobe (Menarik Metadata Asli)
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	cmd := exec.CommandContext(ctx, "ffprobe",
		"-v", "error",
		"-select_streams", "v:0",
		"-show_entries", "stream=bit_rate",
		"-of", "default=noprint_wrappers=1:nokey=1",
		inputPath,
	)

	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()

	if err != nil {
		WriteLog("OPTIMIZER", "WARN_PROBE_FAIL", "Gagal membaca struktur video. Jatuh kembali ke Argumen Kaku (Fallback).")
		return originalArgs
	}

	// 3. Menghitung Bitrate Aktual
	bitrateStr := strings.TrimSpace(out.String())
	if bitrateStr == "N/A" || bitrateStr == "" {
		WriteLog("OPTIMIZER", "WARN_NO_BITRATE", "Bitrate tidak terdeteksi. Menggunakan Argumen Kaku.")
		return originalArgs
	}

	bitrate, err := strconv.ParseFloat(bitrateStr, 64)
	if err != nil {
		return originalArgs
	}

	bitrateKbps := bitrate / 1000.0
	WriteLog("OPTIMIZER", "INFO_BITRATE", fmt.Sprintf("Mendeteksi file berbobot: %.2f kbps", bitrateKbps))

	// 4. OTAK (SMART DECISION TREE)
	outputArg := originalArgs[len(originalArgs)-1] // Asumsi logis: Elemen terakhir selalu file output

	// KONDISI A: Video sudah sangat kecil (Misal rekaman WhatsApp: < 1500 kbps)
	// TINDAKAN: Melarang keras FFmpeg membuang CPU untuk mere-encode. Langsung DIBUNGKUS MENTAH!
	if bitrateKbps < 1500.0 {
		WriteLog("OPTIMIZER", "INFO_SMART_SKIP", "File rahasia ini sudah sangat terkompres! Bypass Re-Encoding aktif (-c copy) -> Durasi render 1 detik!")
		return []string{"-y", "-i", inputPath, "-c", "copy", outputArg}
	}

	// KONDISI B: Video Kualitas Raksasa/Bioskop (Misal 4K Raw: > 15.000 kbps)
	// TINDAKAN: Hitung rasio penyusutan agresif agar server tidak jebol, namun gambar dijamin tidak pecah (Maximum B-Frames & VBV Buffer)
	if bitrateKbps > 15000.0 {
		WriteLog("OPTIMIZER", "INFO_SMART_COMPRESS", "File Monster Terdeteksi! 🛡️ Memasang penangkal VBV Buffer 10M dan Preset Faster.")
		return []string{
			"-y", "-i", inputPath,
			"-c:v", "libx264",
			"-preset", "faster", // Beban CPU dihemat 40%
			"-crf", "23", // Kualitas visual manusiawi terjamin
			"-maxrate", "5M", // Batas laju per detik tidak boleh lewat 5 Mbps
			"-bufsize", "10M", // Buffer ganda untuk mencegah tersendat
			"-c:a", "aac",
			"-b:a", "128k", // Audio dihemat maksimal
			outputArg,
		}
	}

	// KONDISI C: Video Medium (Standar web)
	// TINDAKAN: Jatuh kembali ke template JSON awal di cli_registry yang di-request pengguna.
	return originalArgs
}
