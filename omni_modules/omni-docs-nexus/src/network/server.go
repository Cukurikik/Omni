package network

import (
	"fmt"
	"omni-bridge/system/fs" // Bridge ke fs_reader.rs via UAST OMNI
	"omni-bridge/ui/layout" // Bridge ke UI TypeScript
)

/// Menjalankan peladen HTTP/3 yang ultra-cepat menggunakan goroutines.
///
/// @since 1.0.0
/// @tags ["network", "concurrency"]
func SpinServer(port int) {
	fmt.Printf("OMNI-DOCS-NEXUS 🚀 memutar peladen di port %d\n", port)
	
	server := omniServer.NewH3Server(port)

	server.OnRequest("GET", "/docs/:module/:page", func(req HttpRequest, res HttpResponse) {
		// Panggil goroutine spawn task
		go func() {
			module := req.Params["module"]
			page := req.Params["page"]
			path := fmt.Sprintf("/omni_modules/%s/docs/%s.md", module, page)

			// Meminta memory pointer (Zero-Copy) dari Rust
			ptr, size, err := fs.read_markdown_zero_copy(path)
			
			if err != nil {
				res.SendStatus(404)
				return
			}
			defer fs.dealloc(ptr)

			// Bridge ke UI renderer (TypeScript AST)
			htmlOutput := layout.RenderDashboard(ptr, size)
			
			// Lepaskan ke TCP Socket
			res.SetHeader("Content-Type", "text/html; charset=utf-8")
			res.SendBinaryStream(htmlOutput)
		}()
	})

	server.Listen()
}
