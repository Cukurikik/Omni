package core

import (
	"fmt"
	"log"
	"strings"
)

// ==========================================
// 🎨 OMNI-CHAMELEON: CSS FRAMEWORK INJECTION ENGINE
// ==========================================
// Injeksi framework CSS (Tailwind/Bootstrap/Bulma) secara otomatis
// ke output SSR tanpa developer perlu config apa-apa.
//
// Konfigurasi: appconfig.json → "ui.css_framework"
//   - "tailwind"  → Tailwind CSS v3 via CDN Play
//   - "bootstrap" → Bootstrap 5.3 via CDN
//   - "bulma"     → Bulma CSS via CDN
//   - "none"      → Tanpa CSS framework (custom styling)
//
// + OMNI-MOTION: View Transitions API untuk animasi sinematik
//   appconfig.json → "ui.view_transitions": true
//   Menginjeksi meta tag dan script untuk page transitions
// ==========================================

// CSSFrameworkConfig menyimpan konfigurasi CSS injection aktif
type CSSFrameworkConfig struct {
	Framework       string
	ViewTransitions bool
	HeadInjection   string // HTML yang akan di-inject ke <head>
	BodyInjection   string // HTML/Scripts yang akan di-inject ke akhir <body>
}

var activeCSSConfig *CSSFrameworkConfig

// ==========================================
// CDN URLs (Selalu gunakan versi terbaru yang stabil)
// ==========================================

var cssFrameworks = map[string]struct {
	Head string
	Body string
}{
	"tailwind": {
		Head: `<script src="https://cdn.tailwindcss.com"></script>`,
		Body: "",
	},
	"bootstrap": {
		Head: `<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YcnS/1vQ+tCI+cF0LYGlRkHp/VCwLJ5LeWHB" crossorigin="anonymous">`,
		Body: `<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>`,
	},
	"bulma": {
		Head: `<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css">`,
		Body: "",
	},
}

// View Transitions API injection
const viewTransitionsMeta = `<meta name="view-transition" content="same-origin">`
const viewTransitionsScript = `<script>
// OMNI-MOTION: View Transitions API
if (document.startViewTransition) {
  document.addEventListener('click', (e) => {
    const link = e.target.closest('a[href]');
    if (!link || link.target === '_blank') return;
    const href = link.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('http')) return;
    e.preventDefault();
    document.startViewTransition(() => {
      window.location.href = href;
    });
  });
}
</script>
<style>
/* OMNI-MOTION: Smooth page transitions */
::view-transition-old(root) {
  animation: 0.3s ease-out both fade-out, 0.3s ease-out both slide-to-left;
}
::view-transition-new(root) {
  animation: 0.3s ease-in both fade-in, 0.3s ease-in both slide-from-right;
}
@keyframes fade-in { from { opacity: 0; } }
@keyframes fade-out { to { opacity: 0; } }
@keyframes slide-from-right { from { transform: translateX(30px); } }
@keyframes slide-to-left { to { transform: translateX(-30px); } }
</style>`

// ==========================================
// PUBLIC API
// ==========================================

// InitChameleon membaca konfigurasi UI dan menyiapkan injection
func InitChameleon() {
	framework := "none"
	viewTransitions := false

	if AppConfig != nil {
		if AppConfig.UI.CSSFramework != "" {
			framework = strings.ToLower(AppConfig.UI.CSSFramework)
		}
		viewTransitions = AppConfig.UI.ViewTransitions
	}

	config := &CSSFrameworkConfig{
		Framework:       framework,
		ViewTransitions: viewTransitions,
	}

	// Bangun injection HTML
	headParts := []string{}
	bodyParts := []string{}

	// CSS Framework injection
	if fw, ok := cssFrameworks[framework]; ok {
		if fw.Head != "" {
			headParts = append(headParts, fw.Head)
		}
		if fw.Body != "" {
			bodyParts = append(bodyParts, fw.Body)
		}
		log.Printf("🎨 [OMNI-CHAMELEON] CSS Framework: %s (CDN Injection)", strings.ToUpper(framework))
	} else if framework != "none" && framework != "" {
		log.Printf("⚠️ [OMNI-CHAMELEON] Framework '%s' tidak dikenali. Opsi: tailwind, bootstrap, bulma, none", framework)
	} else {
		log.Println("🎨 [OMNI-CHAMELEON] CSS Framework: NONE (Custom styling)")
	}

	// View Transitions API injection
	if viewTransitions {
		headParts = append(headParts, viewTransitionsMeta)
		bodyParts = append(bodyParts, viewTransitionsScript)
		log.Println("🎬 [OMNI-MOTION] View Transitions API: AKTIF (Sinematik page transitions)")
	}

	config.HeadInjection = strings.Join(headParts, "\n")
	config.BodyInjection = strings.Join(bodyParts, "\n")

	activeCSSConfig = config
}

// GetChameleonHeadInjection mengembalikan HTML yang harus di-inject ke <head>
// Digunakan oleh SSR engine (ssr_engine.go) saat merender halaman
func GetChameleonHeadInjection() string {
	if activeCSSConfig == nil {
		return ""
	}
	return activeCSSConfig.HeadInjection
}

// GetChameleonBodyInjection mengembalikan HTML yang harus di-inject sebelum </body>
func GetChameleonBodyInjection() string {
	if activeCSSConfig == nil {
		return ""
	}
	return activeCSSConfig.BodyInjection
}

// GetChameleonStatus mengembalikan string status untuk banner
func GetChameleonStatus() string {
	if activeCSSConfig == nil {
		return "OFF"
	}

	parts := []string{}
	if activeCSSConfig.Framework != "none" && activeCSSConfig.Framework != "" {
		parts = append(parts, strings.ToUpper(activeCSSConfig.Framework))
	} else {
		parts = append(parts, "Custom CSS")
	}

	if activeCSSConfig.ViewTransitions {
		parts = append(parts, "+ MOTION")
	}

	return strings.Join(parts, " ")
}

// InjectToHTML menginjeksi CSS framework dan View Transitions ke HTML mentah.
// Mengembalikan HTML yang sudah terinjeksi.
//
// Contoh:
//
//	html := core.InjectToHTML("<html><head></head><body>Hello</body></html>")
//	// → HTML dengan CDN Tailwind di <head> dan View Transitions script di <body>
func InjectToHTML(rawHTML string) string {
	if activeCSSConfig == nil {
		return rawHTML
	}

	result := rawHTML

	// Inject ke <head>
	if activeCSSConfig.HeadInjection != "" {
		result = strings.Replace(result, "</head>",
			fmt.Sprintf("%s\n</head>", activeCSSConfig.HeadInjection), 1)
	}

	// Inject ke <body> (sebelum </body>)
	if activeCSSConfig.BodyInjection != "" {
		result = strings.Replace(result, "</body>",
			fmt.Sprintf("%s\n</body>", activeCSSConfig.BodyInjection), 1)
	}

	return result
}
