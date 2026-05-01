package routes

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"time"

	"omnitools/services"
)

// OmniToolRegistry maps tool IDs to their actual handler functions.
// Replaces the Ghost OracleMockRoutes with production-grade dispatch.
type ToolHandler func(toolID string, params map[string]string) (map[string]interface{}, error)

var OmniToolRegistry = make(map[string]ToolHandler)

func init() {
	// Register all production tool handlers here
	OmniToolRegistry["video_compress"] = handleVideoCompress
	OmniToolRegistry["audio_transcode"] = handleAudioTranscode
	OmniToolRegistry["image_resize"] = handleImageResize
	OmniToolRegistry["pdf_merge"] = handlePdfMerge
	OmniToolRegistry["text_analyze"] = handleTextAnalyze
}

// UniversalExecuteHandler is the production replacement for OracleMockRoutes.
// Routes to actual tool implementations instead of returning mock responses.
func UniversalExecuteHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Parse request body
	var req struct {
		ToolID string            `json:"tool_id"`
		Params map[string]string `json:"params"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"error":   "ERR_INVALID_JSON",
			"message": "Request body must be valid JSON",
		})
		return
	}

	if req.ToolID == "" {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"error":   "ERR_NO_TOOL_ID",
			"message": "Parameter 'tool_id' is required",
		})
		return
	}

	// Look up handler in registry
	handler, exists := OmniToolRegistry[req.ToolID]
	if !exists {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"error":   "ERR_TOOL_NOT_FOUND",
			"message": fmt.Sprintf("Tool '%s' not found", req.ToolID),
		})
		return
	}

	// Execute the actual tool
	startTime := time.Now()
	result, err := handler(req.ToolID, req.Params)
	latency := time.Since(startTime)

	if err != nil {
		log.Printf("[ERROR] Tool %s execution failed after %v: %v", req.ToolID, latency, err)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success":    false,
			"error":      "ERR_EXECUTION_FAILED",
			"message":    err.Error(),
			"latency_ms": latency.Milliseconds(),
		})
		return
	}

	// Add metadata to response
	result["tool_id"] = req.ToolID
	result["latency_ms"] = latency.Milliseconds()
	result["timestamp"] = time.Now().Format(time.RFC3339)

	services.WriteLog("TOOL_EXECUTOR", "OK", fmt.Sprintf("Tool %s executed in %v", req.ToolID, latency))

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(result)
}

// ==========================================
// TOOL HANDLER IMPLEMENTATIONS
// ==========================================

func handleVideoCompress(toolID string, params map[string]string) (map[string]interface{}, error) {
	return nil, fmt.Errorf("video_compress: implementation pending — connect to FFmpeg WASM engine")
}

func handleAudioTranscode(toolID string, params map[string]string) (map[string]interface{}, error) {
	return nil, fmt.Errorf("audio_transcode: implementation pending — connect to audio engine")
}

func handleImageResize(toolID string, params map[string]string) (map[string]interface{}, error) {
	return nil, fmt.Errorf("image_resize: implementation pending — connect to image engine")
}

func handlePdfMerge(toolID string, params map[string]string) (map[string]interface{}, error) {
	return nil, fmt.Errorf("pdf_merge: implementation pending — connect to PDF engine")
}

func handleTextAnalyze(toolID string, params map[string]string) (map[string]interface{}, error) {
	if params == nil {
		return nil, fmt.Errorf("text_analyze: 'text' parameter required")
	}

	text, ok := params["text"]
	if !ok || text == "" {
		return nil, fmt.Errorf("text_analyze: 'text' parameter cannot be empty")
	}

	// Real text analysis
	wordCount := len(strings.Fields(text))
	charCount := len(text)
	sentenceCount := 0
	for _, ch := range text {
		if ch == '.' || ch == '!' || ch == '?' {
			sentenceCount++
		}
	}
	if sentenceCount == 0 && text != "" {
		sentenceCount = 1
	}

	avgWordLen := 0.0
	if wordCount > 0 {
		avgWordLen = float64(charCount) / float64(wordCount)
	}

	return map[string]interface{}{
		"success": true,
		"data": map[string]interface{}{
			"word_count":      wordCount,
			"char_count":      charCount,
			"sentence_count":  sentenceCount,
			"avg_word_length": avgWordLen,
		},
	}, nil
}
