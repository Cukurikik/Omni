package middleware

import (
	"fmt"
	"log"
	"net/http"
	"time"

	"omnitools/services"
)

// ==========================================
// 📊 OMNI REQUEST TELEMETRY MIDDLEWARE
// ==========================================
// Middleware ini membungkus setiap request HTTP dengan:
// - Logging terstruktur (method, path, status, latency)
// - Distributed tracing (TraceID header injection)
// - Atomic counter untuk dashboard real-time

// TelemetryMiddleware membungkus handler dengan metrik otomatis
func TelemetryMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		telemetry := services.GetTelemetry()

		// Mulai trace span
		span := telemetry.StartSpan(fmt.Sprintf("%s %s", r.Method, r.URL.Path))

		// Catat request masuk
		telemetry.RecordRequest()
		start := time.Now()

		// Inject TraceID ke response header untuk client-side correlation
		w.Header().Set("X-OMNI-Trace-ID", span.TraceID)
		w.Header().Set("X-OMNI-Span-ID", span.SpanID)

		// Bungkus ResponseWriter untuk menangkap status code
		wrapped := &statusRecorder{ResponseWriter: w, statusCode: 200}

		// Eksekusi handler request sesungguhnya
		next.ServeHTTP(wrapped, r)

		// Hitung durasi
		latency := time.Since(start)
		latencyMs := float64(latency.Microseconds()) / 1000.0

		// Catat selesai
		telemetry.FinishRequest(latencyMs)

		// Catat error jika status >= 400
		if wrapped.statusCode >= 400 {
			telemetry.RecordError()
			telemetry.EndSpan(span, fmt.Errorf("HTTP %d", wrapped.statusCode))
		} else {
			telemetry.EndSpan(span, nil)
		}

		// Structured log
		log.Printf("📊 [REQ] %s %s → %d (%.2fms) [trace:%s]",
			r.Method, r.URL.Path, wrapped.statusCode, latencyMs, span.TraceID)
	})
}

// statusRecorder membungkus http.ResponseWriter untuk menangkap status code
type statusRecorder struct {
	http.ResponseWriter
	statusCode int
}

func (r *statusRecorder) WriteHeader(code int) {
	r.statusCode = code
	r.ResponseWriter.WriteHeader(code)
}
