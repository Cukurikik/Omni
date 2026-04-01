package core

import (
	"encoding/json"
	"net/http"
	"strconv"
)

// OmniContext adalah nyawa dari setiap request
type OmniContext struct {
	W http.ResponseWriter
	R *http.Request
}

// ==========================================
// 📥 REQUEST LAYER (Input Penjinak File Raksasa)
// ==========================================

// ParseBody membaca JSON dengan aman
func (c *OmniContext) ParseBody(dest interface{}) error {
	defer c.R.Body.Close()
	return json.NewDecoder(c.R.Body).Decode(dest)
}

// GetParam mengambil query string dengan fallback
func (c *OmniContext) GetParam(key string, fallback string) string {
	val := c.R.URL.Query().Get(key)
	if val == "" {
		return fallback
	}
	return val
}

// GetIntParam mengambil parameter dalam bentuk angka
func (c *OmniContext) GetIntParam(key string, fallback int) int {
	val := c.R.URL.Query().Get(key)
	if val == "" {
		return fallback
	}
	num, err := strconv.Atoi(val)
	if err != nil {
		return fallback
	}
	return num
}

// ==========================================
// 📤 RESPONSE LAYER (Output Terstandarisasi)
// ==========================================

// JSON mengirim response standar OMNI
func (c *OmniContext) JSON(status int, success bool, message string, data interface{}) {
	c.W.Header().Set("Content-Type", "application/json")
	c.W.WriteHeader(status)
	json.NewEncoder(c.W).Encode(map[string]interface{}{
		"success": success,
		"message": message,
		"data":    data,
	})
}

// SendStream mengirim file video/audio secara streaming (Anti-RAM penuh)
func (c *OmniContext) SendStream(filePath string) {
	// Http.ServeFile sudah otomatis mendukung "Accept-Ranges: bytes"
	// yang dibutuhkan oleh tag <video> dan <audio> di HTML/React.
	http.ServeFile(c.W, c.R, filePath)
}
