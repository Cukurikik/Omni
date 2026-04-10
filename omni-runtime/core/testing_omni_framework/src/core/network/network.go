package network

import (
	"encoding/json"
	"log"
	"net/http"
)

// Request mewakili kontrak payload jaringan OMNI
type Request struct {
	Body map[string]interface{}
}

// Response mewakili balasan absolut OMNI ke client
type Response struct {
	StatusCode int
	Body       map[string]interface{}
}

// Post mendaftarkan OMNI endpoint menggunakan HTTP server bawaan secepat kilat
func Post(path string, handler func(Request) Response) {
	http.HandleFunc(path, func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}

		var body map[string]interface{}
		if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
			w.WriteHeader(http.StatusBadRequest)
			return
		}

		req := Request{Body: body}
		res := handler(req)

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(res.StatusCode)
		json.NewEncoder(w).Encode(res.Body)
	})

	log.Printf("[OMNI-NET] 🚀 Endpoint Pos AKTIF di rute %s", path)
}

// JSON membungkus paket JSON response standar OMNI
func JSON(statusCode int, data map[string]interface{}) Response {
	return Response{
		StatusCode: statusCode,
		Body:       data,
	}
}

// Ignite menyalakan server secara formal
func Ignite(port string) {
	log.Printf("[OMNI-NET] 🔥 Menjalankan Mesin Jaringan OMNI di port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
