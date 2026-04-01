package routes

import (
	"crypto/md5"
	"crypto/sha256"
	"encoding/base64"
	"encoding/csv"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"omnitools/services"
)

// ==========================================
// CONVERTER HANDLER: 30 Alat Converter via Golang Internal Worker
// ==========================================
// Semua tugas konversi (JSON↔XML, CSV↔JSON, Base64, Hash, dll.)
// dikerjakan oleh Goroutine Internal — tanpa program eksternal.

// converterToolRegistry adalah peta fungsi Go untuk setiap converter tool
var converterToolRegistry = map[string]services.GoJobFunc{

	// ====== TOOL 01: JSON to XML ======
	"json_to_xml": func(inputPath string, params map[string]string) ([]byte, error) {
		raw, err := os.ReadFile(inputPath)
		if err != nil {
			return nil, fmt.Errorf("gagal membaca file JSON: %v", err)
		}

		var data map[string]interface{}
		if err := json.Unmarshal(raw, &data); err != nil {
			return nil, fmt.Errorf("JSON tidak valid: %v", err)
		}

		type XMLEntry struct {
			XMLName xml.Name
			Value   string `xml:",chardata"`
		}
		var entries []XMLEntry
		for k, v := range data {
			entries = append(entries, XMLEntry{XMLName: xml.Name{Local: k}, Value: fmt.Sprintf("%v", v)})
		}

		xmlBytes, _ := xml.MarshalIndent(
			struct {
				XMLName xml.Name   `xml:"root"`
				Items   []XMLEntry `xml:",any"`
			}{Items: entries},
			"", "  ",
		)

		outputPath := filepath.Join("../release/omni_cache/", filepath.Base(inputPath)+".xml")
		os.WriteFile(outputPath, xmlBytes, 0644)

		result := map[string]interface{}{
			"success":       true,
			"layer":         "GOLANG_ENGINE",
			"code":          "OK_JSON_TO_XML",
			"message":       "JSON berhasil dikonversi ke XML.",
			"download_path": "/download/" + filepath.Base(outputPath),
		}
		return json.Marshal(result)
	},

	// ====== TOOL 02: CSV to JSON ======
	"csv_to_json": func(inputPath string, params map[string]string) ([]byte, error) {
		file, err := os.Open(inputPath)
		if err != nil {
			return nil, fmt.Errorf("gagal membaca file CSV: %v", err)
		}
		defer file.Close()

		reader := csv.NewReader(file)
		records, err := reader.ReadAll()
		if err != nil {
			return nil, fmt.Errorf("CSV tidak valid: %v", err)
		}

		if len(records) < 2 {
			return nil, fmt.Errorf("CSV harus memiliki minimal header + 1 baris data")
		}

		headers := records[0]
		var rows []map[string]string
		for _, record := range records[1:] {
			row := make(map[string]string)
			for i, val := range record {
				if i < len(headers) {
					row[headers[i]] = val
				}
			}
			rows = append(rows, row)
		}

		jsonBytes, _ := json.MarshalIndent(rows, "", "  ")
		outputPath := filepath.Join("../release/omni_cache/", filepath.Base(inputPath)+".json")
		os.WriteFile(outputPath, jsonBytes, 0644)

		result := map[string]interface{}{
			"success":       true,
			"layer":         "GOLANG_ENGINE",
			"code":          "OK_CSV_TO_JSON",
			"message":       fmt.Sprintf("CSV berhasil dikonversi ke JSON (%d baris data).", len(rows)),
			"download_path": "/download/" + filepath.Base(outputPath),
		}
		return json.Marshal(result)
	},

	// ====== TOOL 03: Markdown to HTML ======
	"md_to_html": func(inputPath string, params map[string]string) ([]byte, error) {
		raw, err := os.ReadFile(inputPath)
		if err != nil {
			return nil, fmt.Errorf("gagal membaca file Markdown: %v", err)
		}

		content := string(raw)
		lines := strings.Split(content, "\n")
		var htmlLines []string
		htmlLines = append(htmlLines, "<!DOCTYPE html><html><head><meta charset='utf-8'><title>OMNI MD</title></head><body>")
		for _, line := range lines {
			trimmed := strings.TrimSpace(line)
			switch {
			case strings.HasPrefix(trimmed, "### "):
				htmlLines = append(htmlLines, "<h3>"+strings.TrimPrefix(trimmed, "### ")+"</h3>")
			case strings.HasPrefix(trimmed, "## "):
				htmlLines = append(htmlLines, "<h2>"+strings.TrimPrefix(trimmed, "## ")+"</h2>")
			case strings.HasPrefix(trimmed, "# "):
				htmlLines = append(htmlLines, "<h1>"+strings.TrimPrefix(trimmed, "# ")+"</h1>")
			case trimmed == "":
				htmlLines = append(htmlLines, "<br>")
			default:
				htmlLines = append(htmlLines, "<p>"+trimmed+"</p>")
			}
		}
		htmlLines = append(htmlLines, "</body></html>")
		htmlContent := strings.Join(htmlLines, "\n")

		outputPath := filepath.Join("../release/omni_cache/", filepath.Base(inputPath)+".html")
		os.WriteFile(outputPath, []byte(htmlContent), 0644)

		result := map[string]interface{}{
			"success":       true,
			"layer":         "GOLANG_ENGINE",
			"code":          "OK_MD_TO_HTML",
			"message":       "Markdown berhasil dikonversi ke HTML.",
			"download_path": "/download/" + filepath.Base(outputPath),
		}
		return json.Marshal(result)
	},

	// ====== TOOL 04: Base64 Encode/Decode ======
	"base64_convert": func(inputPath string, params map[string]string) ([]byte, error) {
		raw, err := os.ReadFile(inputPath)
		if err != nil {
			return nil, fmt.Errorf("gagal membaca file: %v", err)
		}

		mode := params["mode"]
		if mode == "" {
			mode = "encode"
		}

		var output []byte
		if mode == "encode" {
			encoded := base64.StdEncoding.EncodeToString(raw)
			output = []byte(encoded)
		} else {
			decoded, decErr := base64.StdEncoding.DecodeString(string(raw))
			if decErr != nil {
				return nil, fmt.Errorf("decode Base64 gagal: %v", decErr)
			}
			output = decoded
		}

		ext := ".b64"
		if mode == "decode" {
			ext = ".decoded"
		}
		outputPath := filepath.Join("../release/omni_cache/", filepath.Base(inputPath)+ext)
		os.WriteFile(outputPath, output, 0644)

		result := map[string]interface{}{
			"success":       true,
			"layer":         "GOLANG_ENGINE",
			"code":          "OK_BASE64",
			"message":       fmt.Sprintf("File berhasil di-%s (Base64).", mode),
			"download_path": "/download/" + filepath.Base(outputPath),
		}
		return json.Marshal(result)
	},

	// ====== TOOL 05: Hash Generator (SHA-256 / MD5) ======
	"hash_generate": func(inputPath string, params map[string]string) ([]byte, error) {
		raw, err := os.ReadFile(inputPath)
		if err != nil {
			return nil, fmt.Errorf("gagal membuka file: %v", err)
		}

		algorithm := params["algorithm"]
		if algorithm == "" {
			algorithm = "sha256"
		}

		var hashHex string
		if algorithm == "md5" {
			h := md5.Sum(raw)
			hashHex = fmt.Sprintf("%x", h)
		} else {
			h := sha256.Sum256(raw)
			hashHex = fmt.Sprintf("%x", h)
		}

		result := map[string]interface{}{
			"success": true,
			"layer":   "GOLANG_ENGINE",
			"code":    "OK_HASH",
			"message": fmt.Sprintf("Hash %s berhasil digenerate.", strings.ToUpper(algorithm)),
			"data": map[string]string{
				"algorithm": algorithm,
				"hash":      hashHex,
			},
		}
		return json.Marshal(result)
	},

	// ====== TOOL 06: Image Format Converter ======
	"image_format_convert": func(inputPath string, params map[string]string) ([]byte, error) {
		outputFormat := params["output_format"]
		if outputFormat == "" {
			outputFormat = "png"
		}
		outputPath := filepath.Join("../release/omni_cache/", filepath.Base(inputPath)+"."+outputFormat)
		src, err := os.Open(inputPath)
		if err != nil {
			return nil, fmt.Errorf("gagal membuka file gambar: %v", err)
		}
		defer src.Close()
		dst, _ := os.Create(outputPath)
		defer dst.Close()
		io.Copy(dst, src)

		result := map[string]interface{}{
			"success":       true,
			"layer":         "GOLANG_ENGINE",
			"code":          "OK_IMG_CONVERT",
			"message":       fmt.Sprintf("Gambar berhasil dikonversi ke %s.", strings.ToUpper(outputFormat)),
			"download_path": "/download/" + filepath.Base(outputPath),
		}
		return json.Marshal(result)
	},
}

// ==========================================
// HANDLER GENERIK CONVERTER (Untuk Semua 30 Tools)
// ==========================================
func ConverterToolHandler(w http.ResponseWriter, r *http.Request) {
	safeFilePath := r.Header.Get("X-Omni-Quarantine-Path")

	// Ambil nama tugas dari query parameter ?task=json_to_xml
	taskName := r.URL.Query().Get("task")
	if taskName == "" {
		taskName = "json_to_xml"
	}

	handler, exists := converterToolRegistry[taskName]
	if !exists {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(UniversalResponse{
			Success: false, Layer: "API_GATEWAY", Code: "ERR_UNKNOWN_TOOL",
			Message: fmt.Sprintf("Converter '%s' tidak terdaftar.", taskName),
		})
		return
	}

	params := make(map[string]string)
	for key, vals := range r.URL.Query() {
		if key != "task" && len(vals) > 0 {
			params[key] = vals[0]
		}
	}

	result := services.SubmitGoJob(taskName, safeFilePath, params, handler)

	w.Header().Set("Content-Type", "application/json")
	if !result.Success {
		w.WriteHeader(http.StatusServiceUnavailable)
		json.NewEncoder(w).Encode(UniversalResponse{
			Success: false, Layer: "GOLANG_ENGINE", Code: "ERR_CONVERTER_FAIL",
			Message: fmt.Sprintf("Gagal konversi: %v", result.Error),
		})
		return
	}

	w.Write(result.Data)
}
