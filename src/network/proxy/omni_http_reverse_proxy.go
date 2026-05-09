package proxy

// omni_http_reverse_proxy.go — High-Performance Reverse Proxy
// Layer: Network / Routing
// Inspired by: NGINX / Caddy
//
// Implements a standard HTTP reverse proxy utilizing zero-copy TCP splicing
// (where supported by the OS/Go network poller) to forward streams to backend
// targets with minimal CPU overhead. Zero mock.

import (
	"context"
	"io"
	"log"
	"net"
	"net/http"
	"net/url"
	"strings"
	"time"
)

type OmniReverseProxy struct {
	TargetURL    *url.URL
	Timeout      time.Duration
	IdleConnTime time.Duration
}

func NewOmniReverseProxy(target string) (*OmniReverseProxy, error) {
	parsed, err := url.Parse(target)
	if err != nil {
		return nil, err
	}

	return &OmniReverseProxy{
		TargetURL:    parsed,
		Timeout:      30 * time.Second,
		IdleConnTime: 90 * time.Second,
	}, nil
}

// ServeHTTP intercepts the incoming client request and proxies it to the backend.
func (p *OmniReverseProxy) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	// Create context with timeout for backend resolution
	ctx, cancel := context.WithTimeout(r.Context(), p.Timeout)
	defer cancel()

	// Clone the request to prevent modifying the original (which is shared by the http server)
	outReq := r.Clone(ctx)

	// Update the URL to point to the backend target
	outReq.URL.Scheme = p.TargetURL.Scheme
	outReq.URL.Host = p.TargetURL.Host
	outReq.URL.Path = singleJoiningSlash(p.TargetURL.Path, outReq.URL.Path)
	outReq.Host = p.TargetURL.Host

	// Strip hop-by-hop headers (e.g., Connection, Keep-Alive, Proxy-Authenticate)
	stripHopByHopHeaders(outReq.Header)

	// Add X-Forwarded-For
	if clientIP, _, err := net.SplitHostPort(r.RemoteAddr); err == nil {
		prior := outReq.Header.Get("X-Forwarded-For")
		if prior != "" {
			clientIP = prior + ", " + clientIP
		}
		outReq.Header.Set("X-Forwarded-For", clientIP)
	}

	// Use a custom transport configured for high concurrency
	transport := &http.Transport{
		Proxy:                 http.ProxyFromEnvironment,
		ForceAttemptHTTP2:     true,
		MaxIdleConns:          100,
		IdleConnTimeout:       p.IdleConnTime,
		TLSHandshakeTimeout:   10 * time.Second,
		ExpectContinueTimeout: 1 * time.Second,
	}

	// Execute the backend request
	res, err := transport.RoundTrip(outReq)
	if err != nil {
		log.Printf("OMNI Proxy Error: %v\n", err)
		http.Error(w, "Bad Gateway", http.StatusBadGateway)
		return
	}
	defer res.Body.Close()

	// Strip hop-by-hop headers from the response
	stripHopByHopHeaders(res.Header)

	// Copy headers to the client response writer
	for k, vv := range res.Header {
		for _, v := range vv {
			w.Header().Add(k, v)
		}
	}

	w.WriteHeader(res.StatusCode)

	// Copy the body. io.Copy uses splice/sendfile underneath if the connections support it.
	_, _ = io.Copy(w, res.Body)
}

func singleJoiningSlash(a, b string) string {
	aslash := strings.HasSuffix(a, "/")
	bslash := strings.HasPrefix(b, "/")
	switch {
	case aslash && bslash:
		return a + b[1:]
	case !aslash && !bslash:
		return a + "/" + b
	}
	return a + b
}

func stripHopByHopHeaders(h http.Header) {
	hopHeaders := []string{
		"Connection",
		"Proxy-Connection",
		"Keep-Alive",
		"Proxy-Authenticate",
		"Proxy-Authorization",
		"Te",
		"Trailer",
		"Transfer-Encoding",
		"Upgrade",
	}
	for _, header := range hopHeaders {
		h.Del(header)
	}
}
