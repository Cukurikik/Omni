package cloud_apis

import (
	"context"
	"fmt"
	"log"

	dialogflow "cloud.google.com/go/dialogflow/apiv2"
	"cloud.google.com/go/dialogflow/apiv2/dialogflowpb"
)

// ==========================================
// 💬 OMNI DIALOGFLOW — CONVERSATIONAL AI
// ==========================================
// Dialogflow menyediakan natural language understanding (NLU).
//
// OMNI Framework menggunakannya untuk:
//   - Chatbot dan voice bot cerdas
//   - Intent detection dari text/audio input
//   - OMNI Telepathy Engine fallback NLU
// ==========================================

// DialogflowBridge menyediakan akses ke agent Dialogflow
type DialogflowBridge struct {
	projectID string
	sessionID string
	language  string
}

// NewDialogflowBridge membuat bridge baru ke Dialogflow Agent
func NewDialogflowBridge(projectID, sessionID, languageCode string) *DialogflowBridge {
	return &DialogflowBridge{
		projectID: projectID,
		sessionID: sessionID,
		language:  languageCode,
	}
}

// sessionPath menghasilkan fully qualified session path
func (d *DialogflowBridge) sessionPath() string {
	return fmt.Sprintf("projects/%s/agent/sessions/%s", d.projectID, d.sessionID)
}

// DetectIntent menganalisis teks pengguna dan mengembalikan intent yang sesuai
func (d *DialogflowBridge) DetectIntent(ctx context.Context, text string) (*dialogflowpb.DetectIntentResponse, error) {
	client, err := dialogflow.NewSessionsClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_DIALOGFLOW_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &dialogflowpb.DetectIntentRequest{
		Session: d.sessionPath(),
		QueryInput: &dialogflowpb.QueryInput{
			Input: &dialogflowpb.QueryInput_Text{
				Text: &dialogflowpb.TextInput{
					Text:         text,
					LanguageCode: d.language,
				},
			},
		},
	}

	resp, err := client.DetectIntent(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("OMNI_DIALOGFLOW_ERROR: gagal mendeteksi intent: %v", err)
	}

	if resp.QueryResult != nil {
		log.Printf("💬 [OMNI DIALOGFLOW] Intent terdeteksi: %s (Confidence: %.2f)",
			resp.QueryResult.Intent.DisplayName, resp.QueryResult.IntentDetectionConfidence)
	}

	return resp, nil
}
