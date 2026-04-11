package cloud_apis

import (
	"context"
	"fmt"
	"log"

	"cloud.google.com/go/vertexai/genai"
)

// ==========================================
// ☁️ OMNI CLOUD APIs: GCP Vertex AI (Gemini)
// ==========================================
// Menyediakan sambungan real-time dan inferensi multi-modal
// untuk Modul Telepathy Code Healing dan OMNI AI Music Models.

type OmniVertexClient struct {
	client *genai.Client
	ctx    context.Context
}

var VertexEngine *OmniVertexClient

// InitializeVertexClient membuka portal REST/gRPC ke Google AI
func InitializeVertexClient(projectID, location string) error {
	ctx := context.Background()

	// Inisialisasi Murni: Menyedot Kredensial Langsung ke Server GCP
	client, err := genai.NewClient(ctx, projectID, location)
	if err != nil {
		return fmt.Errorf("omni-gcp: gagal membuat klien Vertex AI: %v", err)
	}

	VertexEngine = &OmniVertexClient{
		client: client,
		ctx:    ctx,
	}

	log.Println("✅ [CLOUD APIs] Otak Buatan Google Vertex AI Tersambung dengan OMNI!")
	return nil
}

// TelepathyInvoke merangsang model Gemini 1.5 Flash untuk membaca Prompt dan AST OMNI
// Ini menggantikan model bridging nodejs di `telepathy_vertex.js` dengan performa Golang Murni.
func (v *OmniVertexClient) TelepathyInvoke(promptSystem, userPayload string) (string, error) {
	if v.client == nil {
		return "", fmt.Errorf("OMNI-Vertex Engine uninitialized")
	}

	// Pilih model mutakhir untuk Code Generation dan Penalaran Super Kilat
	model := v.client.GenerativeModel("gemini-1.5-flash-preview")
	
	// Set temperatur agar selalu konsisten untuk output PGO Compiler 
	temperature := float32(0.2)
	model.SetTemperature(temperature)
	model.SetMaxOutputTokens(2048)

	// Persiapkan input konteks OMNI
	prompt := fmt.Sprintf("%s\n\nPayload:\n%s", promptSystem, userPayload)

	log.Printf("🧠 [API VERTEX] Mengirim %d byte konteks neural ke Gemini...", len(prompt))

	resp, err := model.GenerateContent(v.ctx, genai.Text(prompt))
	if err != nil {
		return "", fmt.Errorf("gemini gagal menerjemahkan ulasan saraf: %v", err)
	}

	if len(resp.Candidates) == 0 || len(resp.Candidates[0].Content.Parts) == 0 {
		return "", fmt.Errorf("gemini merespons dengan konten kosong")
	}

	// Parse Extract String Content (PGO Tuning / Logika Bisnis)
	var generatedText string
	for _, part := range resp.Candidates[0].Content.Parts {
		if textPart, ok := part.(genai.Text); ok {
			generatedText += string(textPart)
		}
	}

	return generatedText, nil
}
