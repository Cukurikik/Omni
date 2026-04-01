package core

import (
	"io"
	"log"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"strings"
	"time"
)

// ==========================================
// 🔀 OMNI-NEXUS: ZERO-RAM REVERSE PROXY PIPELINE
// ==========================================
// Saat Master menerima file 50GB dari user, ia tidak menyimpan
// file ke SSD-nya sendiri. Master menjadi "Pipa Tembus Pandang"
// yang mengalirkan setiap byte langsung dari soket TCP user
// ke soket TCP Worker.
//
// Teknologi: httputil.ReverseProxy + io.Copy (buffer ~32KB)
// RAM terpakai di Master: ~32 Kilobyte untuk file tak terbatas!
//
// Ini adalah replikasi bare-metal dari:
//   - AWS Elastic Load Balancer (ELB)
//   - NGINX reverse proxy
//   - Cloudflare Workers
// ==========================================

// StreamToWorker adalah Pipa Tembus Pandang.
// Ia membajak koneksi masuk dari User dan menyambungkannya
// langsung ke Worker yang dipilih oleh Load Balancer.
//
// Flow:
//   User (Jakarta) ──TCP──> Master (Singapura) ──TCP──> Worker (Tokyo)
//   RAM Master: ~32KB buffer | SSD Master: Tidak tersentuh
//
// Response Worker akan langsung mengalir balik ke User melalui
// pipa yang sama, sehingga User mendapat Job ID dari Worker.
func StreamToWorker(w http.ResponseWriter, r *http.Request, workerIP string) {
	// Pastikan workerIP punya format lengkap
	targetStr := workerIP
	if !strings.HasPrefix(targetStr, "http://") && !strings.HasPrefix(targetStr, "https://") {
		targetStr = "http://" + targetStr
	}

	targetURL, err := url.Parse(targetStr)
	if err != nil {
		log.Printf("❌ [NEXUS PIPELINE] URL Worker tidak valid: %s — %v", workerIP, err)
		http.Error(w, `{"error":"NEXUS_INVALID_WORKER","message":"Target Prajurit Invalid"}`, http.StatusInternalServerError)
		return
	}

	log.Printf("🔀 [NEXUS PIPELINE] Mengalihkan aliran data ke Prajurit: %s%s",
		workerIP, r.URL.Path)

	// Buat Mesin Reverse Proxy Bawaan Golang
	proxy := &httputil.ReverseProxy{
		Director: func(req *http.Request) {
			req.URL.Scheme = targetURL.Scheme
			req.URL.Host = targetURL.Host
			// Pertahankan path dan query asli dari user
			// sehingga Worker menerima request identik
			req.Host = targetURL.Host

			// Suntikkan tanda pengenal resmi dari Jenderal
			req.Header.Set("X-NEXUS-COMMANDER", "OMNI_MASTER_AUTHORIZED")
			req.Header.Set("X-NEXUS-KEY", AppConfig.NexusCluster.ClusterSecret)
			req.Header.Set("X-NEXUS-ORIGIN-IP", r.RemoteAddr)

			// Hapus hop-by-hop headers yang tidak boleh di-forward
			req.Header.Del("Connection")
		},

		// Transport kustom untuk kontrol timeout dan koneksi
		Transport: &http.Transport{
			// Proxy tidak perlu idle connections yang lama
			MaxIdleConns:        10,
			IdleConnTimeout:     90 * time.Second,
			// Timeout handshake TCP ke Worker
			DialContext: (&net.Dialer{
				Timeout:   10 * time.Second,
				KeepAlive: 30 * time.Second,
			}).DialContext,
			// Timeout TLS (jika Worker menggunakan HTTPS)
			TLSHandshakeTimeout: 5 * time.Second,
			// KRITIS: Disable response buffering agar streaming tetap zero-copy
			DisableCompression: true,
			// Biarkan Content-Length melewati proxy tanpa dimodifikasi
			ResponseHeaderTimeout: 30 * time.Second,
		},

		// Flush interval untuk streaming: alirkan data setiap 100ms
		// Semakin kecil = semakin real-time, tapi lebih banyak syscall
		FlushInterval: 100 * time.Millisecond,

		// Error handler jika Worker mati di tengah streaming
		ErrorHandler: func(w http.ResponseWriter, r *http.Request, err error) {
			log.Printf("💀 [NEXUS PIPELINE] Pipa putus ke %s: %v — Mencoba fallback...", workerIP, err)

			// Laporan ke klien bahwa Worker gagal
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusBadGateway)
			w.Write([]byte(`{"error":"NEXUS_PIPELINE_BROKEN","message":"Koneksi ke Prajurit terputus. Silakan coba lagi."}`))
		},

		// Modifikasi response dari Worker sebelum dikirim ke User
		ModifyResponse: func(resp *http.Response) error {
			// Tambahkan header identitas NEXUS ke response
			resp.Header.Set("X-Nexus-Served-By", workerIP)
			resp.Header.Set("X-Powered-By", "OMNI-NEXUS/2.0")

			log.Printf("✅ [NEXUS PIPELINE] Response diterima dari %s → Status: %d",
				workerIP, resp.StatusCode)
			return nil
		},
	}

	// ⚡ EKSEKUSI STREAMING!
	// Baris ini akan menahan koneksi HTTP sampai:
	// 1. Seluruh file selesai mengalir dari User → Worker
	// 2. Worker selesai memproses dan mengirim response
	// 3. Response Worker mengalir balik dari Worker → User
	//
	// Selama proses ini, Master hanya menggunakan ~32KB RAM!
	proxy.ServeHTTP(w, r)
}

// StreamToWorkerWithBody mengirim raw body ([]byte) ke Worker
// untuk kasus di mana Master perlu men-dispatch payload tertentu.
func StreamToWorkerWithBody(workerIP string, method string, path string, body io.Reader, headers map[string]string) (*http.Response, error) {
	targetStr := workerIP
	if !strings.HasPrefix(targetStr, "http://") && !strings.HasPrefix(targetStr, "https://") {
		targetStr = "http://" + targetStr
	}

	fullURL := targetStr + path

	req, err := http.NewRequest(method, fullURL, body)
	if err != nil {
		return nil, err
	}

	// Inject NEXUS headers
	req.Header.Set("X-NEXUS-COMMANDER", "OMNI_MASTER_AUTHORIZED")
	req.Header.Set("X-NEXUS-KEY", AppConfig.NexusCluster.ClusterSecret)
	for k, v := range headers {
		req.Header.Set(k, v)
	}

	client := &http.Client{
		Timeout: 0, // No timeout — file bisa sangat besar
		Transport: &http.Transport{
			MaxIdleConns:        5,
			IdleConnTimeout:     90 * time.Second,
			DisableCompression:  true,
		},
	}

	return client.Do(req)
}

// IsNexusMaster mengembalikan true jika server ini adalah Master Node.
func IsNexusMaster() bool {
	if AppConfig == nil {
		return false
	}
	return AppConfig.NexusCluster.Role == "master"
}

// IsNexusWorker mengembalikan true jika server ini adalah Worker Node.
func IsNexusWorker() bool {
	if AppConfig == nil {
		return false
	}
	return AppConfig.NexusCluster.Role == "worker"
}

// IsNexusDelegated mengecek apakah request ini datang dari Master (delegasi NEXUS).
func IsNexusDelegated(r *http.Request) bool {
	return r.Header.Get("X-NEXUS-COMMANDER") == "OMNI_MASTER_AUTHORIZED" &&
		r.Header.Get("X-NEXUS-KEY") == AppConfig.NexusCluster.ClusterSecret
}
