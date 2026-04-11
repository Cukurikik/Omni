package network

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

// SpinServer starts the OMNI-DOCS-NEXUS HTTP server.
//
// Serves markdown documentation files from the omni_modules directory.
// Uses standard Go net/http with goroutine-per-request concurrency.
//
// @since 1.0.0
// @tags ["network", "concurrency"]
func SpinServer(port int) {
	addr := fmt.Sprintf(":%d", port)
	log.Printf("OMNI-DOCS-NEXUS starting on port %d", port)

	mux := http.NewServeMux()

	// Serve documentation pages: /docs/{module}/{page}
	mux.HandleFunc("/docs/", func(w http.ResponseWriter, r *http.Request) {
		// Parse path: /docs/{module}/{page}
		parts := strings.Split(strings.TrimPrefix(r.URL.Path, "/docs/"), "/")
		if len(parts) < 2 {
			http.Error(w, "Usage: /docs/{module}/{page}", http.StatusBadRequest)
			return
		}

		module := parts[0]
		page := parts[1]
		docPath := filepath.Join("omni_modules", module, "docs", page+".md")

		// Read markdown file (zero-copy via OS mmap when available)
		content, err := os.ReadFile(docPath)
		if err != nil {
			http.Error(w, fmt.Sprintf("Document not found: %s/%s", module, page), http.StatusNotFound)
			return
		}

		// Render as HTML with basic markdown wrapper
		html := renderMarkdownPage(module, page, string(content))

		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Header().Set("X-OMNI-Module", module)
		w.WriteHeader(http.StatusOK)
		fmt.Fprint(w, html)
	})

	// Health check endpoint
	mux.HandleFunc("/health", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprint(w, `{"status":"ok","service":"omni-docs-nexus"}`)
	})

	log.Printf("OMNI-DOCS-NEXUS listening on %s", addr)
	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatalf("OMNI-DOCS-NEXUS failed to start: %v", err)
	}
}

// renderMarkdownPage wraps markdown content in a basic HTML page
func renderMarkdownPage(module, page, markdownContent string) string {
	return fmt.Sprintf(`<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>%s — %s | OMNI Docs</title>
    <style>
        body { font-family: 'Inter', system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; }
        pre { background: #1e1e2e; color: #cdd6f4; padding: 1rem; border-radius: 8px; overflow-x: auto; }
        code { font-family: 'JetBrains Mono', monospace; }
    </style>
</head>
<body>
    <nav><a href="/">OMNI Docs</a> / <a href="/docs/%s">%s</a> / %s</nav>
    <article>
        <pre>%s</pre>
    </article>
</body>
</html>`, module, page, module, module, page, markdownContent)
}
