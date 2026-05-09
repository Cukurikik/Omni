package network_go

import (
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"sync/atomic"
)

// OmniMoELoadBalancer acts as a Layer 7 Round-Robin LB sitting in front
// of multiple Go API Gateways.
type OmniMoELoadBalancer struct {
	backends []*url.URL
	current  uint64
}

func NewLoadBalancer(backendUrls []string) *OmniMoELoadBalancer {
	var backends []*url.URL
	for _, u := range backendUrls {
		parsed, err := url.Parse(u)
		if err != nil {
			log.Fatalf("OMNI LB Error parsing backend URL: %v", err)
		}
		backends = append(backends, parsed)
	}

	fmt.Printf("OMNI Go: Initialized L7 Load Balancer with %d Gateway backends.\n", len(backends))

	return &OmniMoELoadBalancer{
		backends: backends,
		current:  0,
	}
}

func (lb *OmniMoELoadBalancer) NextBackend() *url.URL {
	next := atomic.AddUint64(&lb.current, 1)
	idx := next % uint64(len(lb.backends))
	return lb.backends[idx]
}

func (lb *OmniMoELoadBalancer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	backend := lb.NextBackend()
	// log.Printf("OMNI LB: Routing request to %s", backend.Host)

	proxy := httputil.NewSingleHostReverseProxy(backend)

	// Update headers for proper reverse proxying
	r.URL.Host = backend.Host
	r.URL.Scheme = backend.Scheme
	r.Header.Set("X-Forwarded-Host", r.Header.Get("Host"))
	r.Host = backend.Host

	proxy.ServeHTTP(w, r)
}

func main() {
	// Example Gateway cluster
	backends := []string{
		"http://omni-gateway-1:8080",
		"http://omni-gateway-2:8080",
		"http://omni-gateway-3:8080",
	}

	lb := NewLoadBalancer(backends)
	server := &http.Server{
		Addr:    ":80",
		Handler: lb,
	}

	log.Println("OMNI Go: Load Balancer listening on port 80...")
	log.Fatal(server.ListenAndServe())
}

