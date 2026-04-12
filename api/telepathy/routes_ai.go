package telepathy

import (
	"context"

	"omnitools/cloud_apis"
)

// RoutesAI menangani Vertex AI, Vision, Speech, Translate, Dialogflow, Document AI, DLP
func RoutesAI(ctx context.Context, method string, args map[string]interface{}, ok func(interface{}) OmniResponse, fail func(error) OmniResponse) (OmniResponse, bool) {
	projectId, _ := args["projectId"].(string)
	location, _ := args["location"].(string)

	switch method {

	// ── VERTEX AI ───────────────────────────────────────────────────
	case "gcp::VertexAI::TelepathyInvoke":
		promptSystem, _ := args["promptSystem"].(string)
		userPayload, _ := args["userPayload"].(string)
		if cloud_apis.VertexEngine == nil {
			_ = cloud_apis.InitializeVertexClient(projectId, location)
		}
		if cloud_apis.VertexEngine != nil {
			res, err := cloud_apis.VertexEngine.TelepathyInvoke(promptSystem, userPayload)
			if err != nil { return fail(err), true }
			return ok(res), true
		}
		return ok("Vertex AI not initialized"), true

	// ── VISION ──────────────────────────────────────────────────────
	case "gcp::Vision::DetectLabels":
		imageURI, _ := args["imageURI"].(string)
		bridge := cloud_apis.NewVisionBridge(projectId)
		res, err := bridge.DetectLabels(ctx, imageURI)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::Vision::DetectText":
		imageURI, _ := args["imageURI"].(string)
		bridge := cloud_apis.NewVisionBridge(projectId)
		res, err := bridge.DetectText(ctx, imageURI)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── SPEECH ───────────────────────────────────────────────────────
	case "gcp::Speech::Transcribe":
		langCode, _ := args["languageCode"].(string)
		bridge := cloud_apis.NewSpeechBridge(projectId)
		res, err := bridge.Transcribe(ctx, nil, langCode, 16000)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── TRANSLATE ────────────────────────────────────────────────────
	case "gcp::Translate::TranslateText":
		targetLang, _ := args["targetLang"].(string)
		sourceLang, _ := args["sourceLang"].(string)
		textsRaw, _ := args["texts"].([]interface{})
		var texts []string
		for _, t := range textsRaw {
			if s, ok := t.(string); ok { texts = append(texts, s) }
		}
		bridge := cloud_apis.NewTranslateBridge(projectId, location)
		res, err := bridge.TranslateText(ctx, texts, targetLang, sourceLang)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::Translate::DetectLanguage":
		text, _ := args["text"].(string)
		bridge := cloud_apis.NewTranslateBridge(projectId, location)
		lang, confidence, err := bridge.DetectLanguage(ctx, text)
		if err != nil { return fail(err), true }
		return ok(map[string]interface{}{"language": lang, "confidence": confidence}), true

	// ── DIALOGFLOW ──────────────────────────────────────────────────
	case "gcp::Dialogflow::DetectIntent":
		sessionId, _ := args["sessionId"].(string)
		text, _ := args["text"].(string)
		langCode, _ := args["languageCode"].(string)
		bridge := cloud_apis.NewDialogflowBridge(projectId, sessionId, langCode)
		res, err := bridge.DetectIntent(ctx, text)
		if err != nil { return fail(err), true }
		return ok(res), true
	}

	return OmniResponse{}, false
}
