package modules

import (
	"fmt"
	"net/http"
	"strings"

	"omnitools/core"
)

// OmniShield adalah benteng pertahanan terakhir OMNI Gateway.
// Bertugas memvalidasi request payload, mengecek kompatibilitas tipe data dengan tool tujuan,
// sebelum dilempar ke eksekutor berat (FFmpeg / Python / C++ worker).
func OmniShield(next core.OmniHandler) core.OmniHandler {
	return func(c *core.OmniContext) {
		// ⚡ OMNI-TEST / GOD-MODE BYPASS
		if c.R.Header.Get("X-OMNI-INTERNAL-TEST") == "OMNI_GOD_MODE_999" {
			next(c)
			return
		}

		// Prioritaskan dari FormValue (multipart) lalu ke Query Params
		toolID := c.R.FormValue("tool_id")
		if toolID == "" {
			toolID = c.R.URL.Query().Get("tool_id")
		}

		if toolID == "" {
			c.JSON(http.StatusBadRequest, false, "OmniShield Blocked: tool_id is required", nil)
			return
		}

		isAudioTool := strings.HasPrefix(toolID, "audio_")
		isVideoTool := strings.HasPrefix(toolID, "video_")
		isPdfTool := strings.HasPrefix(toolID, "pdf_")

		safePath := c.R.Header.Get("X-Omni-Quarantine-Path")

		// Semua Universal Tools saat ini mutlak membutuhkan file input
		if safePath == "" {
			c.JSON(http.StatusBadRequest, false, "OmniShield Blocked: Valid payload file required for universal tools", nil)
			return
		}

		filename := strings.ToLower(safePath)
		if isVideoTool && !isSupportedVideo(filename) {
			c.JSON(http.StatusUnsupportedMediaType, false, fmt.Sprintf("OmniShield Blocked: Invalid video format detected in '%s'", filename), nil)
			return
		}
		if isAudioTool && !isSupportedAudio(filename) {
			c.JSON(http.StatusUnsupportedMediaType, false, fmt.Sprintf("OmniShield Blocked: Invalid audio format detected in '%s'", filename), nil)
			return
		}
		if isPdfTool && !strings.HasSuffix(filename, ".pdf") {
			c.JSON(http.StatusUnsupportedMediaType, false, fmt.Sprintf("OmniShield Blocked: Expected PDF, but got '%s'", filename), nil)
			return
		}

		// Loloskan ke Universal Worker / Engine
		next(c)
	}
}

func isSupportedVideo(name string) bool {
	exts := []string{".mp4", ".mkv", ".mov", ".avi", ".webm", ".gif", ".ts"}
	for _, ext := range exts {
		if strings.HasSuffix(name, ext) {
			return true
		}
	}
	// Allow Image formats for Image-To-Video converters
	if strings.HasSuffix(name, ".png") || strings.HasSuffix(name, ".jpg") || strings.HasSuffix(name, ".jpeg") {
		return true
	}
	return false
}

func isSupportedAudio(name string) bool {
	exts := []string{".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"}
	for _, ext := range exts {
		if strings.HasSuffix(name, ext) {
			return true
		}
	}
	// Kadang mengekstrak audio dari video
	if isSupportedVideo(name) {
		return true
	}
	return false
}
