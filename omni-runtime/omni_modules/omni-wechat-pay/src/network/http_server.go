package omni_wechat_pay

import (
	"context"
	"net/http"
	"time"
	"fmt"
)

type HTTPServer struct {
	server *http.Server
	mux    *http.ServeMux
	port   int
}

func NewHTTPServer(port int) *HTTPServer {
	mux := http.NewServeMux()
	return &HTTPServer{
		server: &http.Server{Addr: fmt.Sprintf(":%d", port), Handler: mux, ReadTimeout: 30 * time.Second, WriteTimeout: 30 * time.Second, IdleTimeout: 120 * time.Second},
		mux: mux, port: port,
	}
}

func (s *HTTPServer) Handle(pattern string, handler http.HandlerFunc) { s.mux.HandleFunc(pattern, handler) }

func (s *HTTPServer) Start() error { return s.server.ListenAndServe() }

func (s *HTTPServer) Shutdown(ctx context.Context) error { return s.server.Shutdown(ctx) }

func (s *HTTPServer) HealthCheck() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("{\"status\":\"healthy\",\"module\":\"omni-wechat-pay\"}"))
	}
}