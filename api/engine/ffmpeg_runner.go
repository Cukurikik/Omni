package engine

import (
	"bytes"
	"context"
	"fmt"
	"log"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"time"

	"omnitools/core"
	"omnitools/services"
)

// ProcessFFmpeg merakit tugas untuk dikirim ke algojo FFmpeg
func ProcessFFmpeg(job *core.Job) ([]byte, error) {
	// Karena CLI sudah merakit argumen lengkap di job.Args, 
	// kita tinggal meneruskannya ke eksekutor utama.
	return services.ExecuteEngineWithTimeout(job.EngineCmd, job.Args, job.Timeout)
}

// ==========================================
// ⚙️ OMNI ENGINE: FFMPEG THROTTLE RUNNER
// ==========================================
// FFmpeg yang dirantai! Membatasi CPU/thread agar tidak melahap
// seluruh sumber daya server saat banyak user aktif bersamaan.
//
// Filosofi: "Berikan setiap pekerjaan jatah wajar, bukan seluruh kerajaan."
// ==========================================

// FFmpegConfig mengkonfigurasi eksekusi FFmpeg yang aman
type FFmpegConfig struct {
	InputPath    string
	OutputPath   string
	ExtraArgs    []string      // Argumen tambahan (filter, codec, dll)
	MaxThreads   int           // Maks thread CPU (default: 2)
	Timeout      time.Duration // Timeout eksekusi (default: 30 menit)
	Preset       string        // Preset encoding (ultrafast/fast/medium/slow)
	OverwriteOut bool          // Timpa output jika sudah ada (-y)
}

// DefaultConfig mengembalikan konfigurasi aman untuk server produksi
func DefaultConfig(inputPath, outputPath string) FFmpegConfig {
	maxThreads := 2
	cpuCount := runtime.NumCPU()
	if cpuCount >= 8 {
		maxThreads = 4 // Server besar boleh pakai lebih
	}

	return FFmpegConfig{
		InputPath:    inputPath,
		OutputPath:   outputPath,
		MaxThreads:   maxThreads,
		Timeout:      30 * time.Minute,
		Preset:       "fast",
		OverwriteOut: true,
	}
}

// RunFFmpegSafe menjalankan FFmpeg dengan pembatasan sumber daya:
// - Thread CPU dibatasi agar tidak menghabiskan seluruh core
// - Timeout agar proses zombie tidak hidup selamanya
// - Logging otomatis untuk monitoring
func RunFFmpegSafe(cfg FFmpegConfig) error {
	// Bangun argumen FFmpeg
	args := []string{
		"-i", cfg.InputPath,
		"-threads", fmt.Sprintf("%d", cfg.MaxThreads),
	}

	// Tambah preset jika ada (untuk video encoding)
	if cfg.Preset != "" {
		args = append(args, "-preset", cfg.Preset)
	}

	// Tambah argumen kustom dari user/tool
	args = append(args, cfg.ExtraArgs...)

	// Timpa output?
	if cfg.OverwriteOut {
		args = append(args, "-y")
	}

	// Output path terakhir
	args = append(args, cfg.OutputPath)

	startTime := time.Now()
	log.Printf("⚙️ [FFMPEG] Memulai: ffmpeg %s", strings.Join(args, " "))

	// INTEGRASI OMNI-CLUSTER: Panggil algojo SSH/prlimit
	out, err := services.ExecuteEngineWithTimeout("ffmpeg", args, cfg.Timeout)
	elapsed := time.Since(startTime)

	if err != nil {
		errMsg := string(out)
		// Ambil 500 karakter terakhir dari error log FFmpeg
		if len(errMsg) > 500 {
			errMsg = errMsg[len(errMsg)-500:]
		}
		log.Printf("❌ [FFMPEG] Gagal (%v): %v", elapsed, err)
		return fmt.Errorf("ffmpeg error: %v - %s", err, errMsg)
	}

	log.Printf("✅ [FFMPEG] Selesai dalam %v: %s → %s", elapsed, filepath.Base(cfg.InputPath), filepath.Base(cfg.OutputPath))
	return nil
}

// RunFFmpegWithProgress menjalankan FFmpeg dan mengembalikan progress via channel.
// Berguna untuk fitur WebSocket real-time progress bar.
func RunFFmpegWithProgress(cfg FFmpegConfig, progressChan chan<- float64) error {
	ctx, cancel := context.WithTimeout(context.Background(), cfg.Timeout)
	defer cancel()
	defer close(progressChan)

	args := []string{
		"-i", cfg.InputPath,
		"-threads", fmt.Sprintf("%d", cfg.MaxThreads),
		"-progress", "pipe:1", // FFmpeg menulis progress ke stdout
		"-nostats", // Tidak usah cetak yang lain
	}

	if cfg.Preset != "" {
		args = append(args, "-preset", cfg.Preset)
	}
	args = append(args, cfg.ExtraArgs...)
	if cfg.OverwriteOut {
		args = append(args, "-y")
	}
	args = append(args, cfg.OutputPath)

	enginePath := "ffmpeg"
	if core.Config != nil && core.Config.FFmpegPath != "" {
		enginePath = core.Config.FFmpegPath
	}

	cmd := exec.CommandContext(ctx, enginePath, args...)

	var stdout bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	err := cmd.Run()

	if ctx.Err() == context.DeadlineExceeded {
		return fmt.Errorf("ffmpeg timeout setelah %v", cfg.Timeout)
	}

	if err != nil {
		return fmt.Errorf("ffmpeg error: %s", stderr.String())
	}

	return nil
}

// QuickConvert melakukan konversi format cepat (tanpa re-encoding jika mungkin)
func QuickConvert(inputPath, outputPath string) error {
	cfg := DefaultConfig(inputPath, outputPath)
	cfg.ExtraArgs = []string{"-c", "copy"} // Stream copy, tanpa re-encoding
	cfg.Preset = ""                        // Tidak perlu preset untuk copy
	return RunFFmpegSafe(cfg)
}

// QuickTrim memotong video/audio berdasarkan waktu mulai dan durasi
func QuickTrim(inputPath, outputPath, startTime, duration string) error {
	cfg := DefaultConfig(inputPath, outputPath)
	cfg.ExtraArgs = []string{
		"-ss", startTime,
		"-t", duration,
		"-c", "copy", // Stream copy untuk kecepatan maksimal
	}
	cfg.Preset = ""
	return RunFFmpegSafe(cfg)
}

// QuickCompress melakukan kompresi video dengan CRF yang dikonfigurasi
func QuickCompress(inputPath, outputPath string, crf int) error {
	cfg := DefaultConfig(inputPath, outputPath)
	cfg.ExtraArgs = []string{
		"-c:v", "libx264",
		"-crf", fmt.Sprintf("%d", crf),
		"-c:a", "aac",
		"-b:a", "128k",
	}
	return RunFFmpegSafe(cfg)
}

// ExtractAudio mengekstrak track audio dari video
func ExtractAudio(inputPath, outputPath string) error {
	cfg := DefaultConfig(inputPath, outputPath)
	cfg.ExtraArgs = []string{"-vn", "-c:a", "copy"}
	cfg.Preset = ""
	return RunFFmpegSafe(cfg)
}

// ExtractThumbnail mengekstrak satu frame dari video sebagai gambar
func ExtractThumbnail(inputPath, outputPath string, timestamp string) error {
	cfg := DefaultConfig(inputPath, outputPath)
	cfg.ExtraArgs = []string{
		"-ss", timestamp,
		"-vframes", "1",
		"-q:v", "2",
	}
	cfg.Preset = ""
	cfg.Timeout = 30 * time.Second // Thumbnail harus cepat
	return RunFFmpegSafe(cfg)
}
