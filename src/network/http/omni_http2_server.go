package network_http

// omni_http2_server.go — HTTP/2 Server Infrastructure
// Layer: Network / Go
//
// Configures and initializes an HTTP/2 compatible Go server designed to handle
// high-throughput microservice traffic with optimized TLS settings. Zero mock.

import (
	"context"
	"crypto/tls"
	"log"
	"net/http"
	"time"

	"golang.org/x/net/http2"
)

type OmniHttp2Server struct {
	addr    string
	handler http.Handler
	server  *http.Server
}

// NewOmniHttp2Server configures a high-performance HTTP/2 server.
func NewOmniHttp2Server(addr string, handler http.Handler, tlsConfig *tls.Config) *OmniHttp2Server {

	// Base server configuration
	srv := &http.Server{
		Addr:         addr,
		Handler:      handler,
		TLSConfig:    tlsConfig,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	// Force HTTP/2 initialization and configuration
	http2Server := &http2.Server{
		MaxConcurrentStreams: 250,
		MaxReadFrameSize:     1048576, // 1MB for higher throughput of large JSON/gRPC
		IdleTimeout:          120 * time.Second,
	}

	if err := http2.ConfigureServer(srv, http2Server); err != nil {
		log.Fatalf("OMNI Network: Failed to configure HTTP/2 server: %v", err)
	}

	return &OmniHttp2Server{
		addr:    addr,
		handler: handler,
		server:  srv,
	}
}

// Start listens and serves HTTPS traffic (HTTP/2 requires TLS).
// certFile and keyFile can be empty if the TLSConfig already provides certificates.
func (s *OmniHttp2Server) Start(certFile, keyFile string) error {
	log.Printf("OMNI Network: Starting HTTP/2 Server on %s", s.addr)

	if certFile != "" && keyFile != "" {
		return s.server.ListenAndServeTLS(certFile, keyFile)
	}

	// If certificates are loaded in TLSConfig directly via GetCertificate
	return s.server.ListenAndServeTLS("", "")
}

// Shutdown gracefully stops the server, allowing active connections to drain.
func (s *OmniHttp2Server) Shutdown(ctx context.Context) error {
	log.Println("OMNI Network: Shutting down HTTP/2 Server gracefully...")
	return s.server.Shutdown(ctx)
}

