package core

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"
	"sync"
)

// ==========================================
// 🌐 OMNI-SSR: SERVER-SIDE RENDERING ENGINE
// ==========================================
// Golang melakukan apa yang Next.js lakukan dengan Node.js,
// tetapi 100x lebih cepat dan hemat RAM.
//
// Alur Kerja:
// 1. Baca index.html hasil Vite Build (SSG)
// 2. Injeksi Meta Tags SEO (OpenGraph, Twitter Cards)
// 3. Injeksi Initial State JSON (React Hydration)
// 4. Kirim HTML lengkap ke browser — Zero Blank Screen!
// ==========================================

// SSRContext berisi data dinamis untuk SEO dan React Hydration
type SSRContext struct {
	Title       string                 `json:"title"`
	Description string                 `json:"description"`
	Image       string                 `json:"image"`
	URL         string                 `json:"url"`
	InitialData map[string]interface{} `json:"initialData,omitempty"`
}

// templateCache menyimpan HTML template di memori (baca file sekali saja)
var (
	templateHTML string
	templateOnce sync.Once
	templateErr  error
)

// DefaultSSRContext mengembalikan meta tag default untuk halaman tanpa konfigurasi khusus
func DefaultSSRContext(requestURL string) SSRContext {
	return SSRContext{
		Title:       "OMNI TOOLS — Enterprise Platform",
		Description: "Platform enterprise hybrid untuk pemrosesan Video, Audio, Image, PDF, dan AI. Didukung oleh Golang bare-metal engine.",
		Image:       "/og-image.png",
		URL:         requestURL,
	}
}

// SSRRouteMetadata adalah mapping route → SEO metadata (hardcoded, cepat)
var SSRRouteMetadata = map[string]SSRContext{
	"/": {
		Title:       "OMNI TOOLS — Dashboard",
		Description: "Dashboard utama OMNI Tools. Akses 150+ tools pemrosesan file enterprise dalam satu platform.",
		Image:       "/og-image.png",
	},
	"/tool/video_trimmer": {
		Title:       "Video Trimmer — OMNI TOOLS",
		Description: "Potong video dengan presisi frame menggunakan FFmpeg engine. Gratis, tanpa upload, sepenuhnya offline.",
		Image:       "/og-video.png",
	},
	"/tool/video_merger": {
		Title:       "Video Merger — OMNI TOOLS",
		Description: "Gabungkan multiple video menjadi satu file dengan transisi mulus. Engine bare-metal C++.",
		Image:       "/og-video.png",
	},
	"/tool/audio_trimmer": {
		Title:       "Audio Trimmer — OMNI TOOLS",
		Description: "Potong audio dengan presisi millisecond menggunakan engine offline.",
		Image:       "/og-audio.png",
	},
	"/tool/pdf_merger": {
		Title:       "PDF Merger — OMNI TOOLS",
		Description: "Gabungkan beberapa file PDF menjadi satu dokumen. Cepat dan aman.",
		Image:       "/og-pdf.png",
	},
}

// loadTemplate membaca index.html dan menyimpannya di memori
func loadTemplate() (string, error) {
	templateOnce.Do(func() {
		// Cari index.html dari release/public (production) atau ui/src (dev)
		paths := []string{
			"../release/public/index.html",
			"../ui/dist/index.html",
		}
		for _, p := range paths {
			data, err := os.ReadFile(p)
			if err == nil {
				templateHTML = string(data)
				return
			}
		}
		templateErr = fmt.Errorf("OMNI-SSR: index.html tidak ditemukan di release/public atau ui/dist")
	})
	return templateHTML, templateErr
}

// ResetSSRCache membersihkan cache template (dipanggil saat rebuild)
func ResetSSRCache() {
	templateOnce = sync.Once{}
	templateHTML = ""
	templateErr = nil
}

// ServeSSR menginjeksi HTML statis dengan kekuatan dinamis Golang
func ServeSSR(w http.ResponseWriter, r *http.Request, ctx SSRContext) {
	// 1. Ambil template HTML (dari cache memori)
	html, err := loadTemplate()
	if err != nil {
		http.Error(w, "SSG Build Not Found — Jalankan 'omni build' terlebih dahulu", 500)
		return
	}

	// 2. INJEKSI SEO META TAGS (Untuk Googlebot, WhatsApp, Twitter)
	metaTags := fmt.Sprintf(`<title>%s</title>
		<meta name="description" content="%s">
		<meta property="og:title" content="%s">
		<meta property="og:description" content="%s">
		<meta property="og:image" content="%s">
		<meta property="og:url" content="%s">
		<meta property="og:type" content="website">
		<meta name="twitter:card" content="summary_large_image">
		<meta name="twitter:title" content="%s">
		<meta name="twitter:description" content="%s">
		<meta name="twitter:image" content="%s">`,
		ctx.Title, ctx.Description,
		ctx.Title, ctx.Description, ctx.Image, ctx.URL,
		ctx.Title, ctx.Description, ctx.Image,
	)

	// Ganti <title> bawaan Vite dengan Meta Tags Dinamis dari Golang
	result := strings.Replace(html, "<title>OMNI TOOLS — Enterprise Platform</title>", metaTags, 1)

	// 3. INJEKSI HYDRATION STATE (React tidak perlu fetching/loading lagi!)
	if ctx.InitialData != nil {
		jsonData, jsonErr := json.Marshal(ctx.InitialData)
		if jsonErr == nil {
			// Simpan data ini di object window browser
			stateScript := fmt.Sprintf(`<script>window.__OMNI_INITIAL_STATE__=%s;</script>`, string(jsonData))
			result = strings.Replace(result, "</head>", stateScript+"\n</head>", 1)
		}
	}

	// 4. Kirim HTML Sempurna ke Pengguna
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	w.Header().Set("X-Powered-By", "OMNI-RENDER-ENGINE/1.0")
	w.Header().Set("X-SSR", "true")

	// COOP/COEP Headers
	w.Header().Set("Cross-Origin-Opener-Policy", "same-origin")
	w.Header().Set("Cross-Origin-Embedder-Policy", "require-corp")
	w.Header().Set("Cross-Origin-Resource-Policy", "cross-origin")

	w.Write([]byte(result))
}

// GetSSRContext mengembalikan SSRContext yang tepat untuk suatu URL path
func GetSSRContext(urlPath string) SSRContext {
	// Cek exact match dulu
	if ctx, ok := SSRRouteMetadata[urlPath]; ok {
		ctx.URL = urlPath
		return ctx
	}

	// Cek prefix match (untuk dynamic routes seperti /tool/*)
	for route, ctx := range SSRRouteMetadata {
		if strings.HasPrefix(urlPath, route) {
			ctx.URL = urlPath
			return ctx
		}
	}

	// Fallback ke default
	return DefaultSSRContext(urlPath)
}

// IsStaticAsset menentukan apakah path adalah file statis (bukan SPA route)
func IsStaticAsset(path string) bool {
	staticExtensions := []string{
		".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
		".woff", ".woff2", ".ttf", ".eot", ".map", ".webp", ".avif",
		".mp4", ".webm", ".mp3", ".wav", ".ogg", ".pdf", ".wasm",
		".json", ".xml", ".txt", ".html",
	}
	pathLower := strings.ToLower(path)
	for _, ext := range staticExtensions {
		if strings.HasSuffix(pathLower, ext) {
			return true
		}
	}
	return false
}
