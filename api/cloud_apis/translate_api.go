package cloud_apis

import (
	"context"
	"fmt"
	"log"

	translate "cloud.google.com/go/translate/apiv3"
	"cloud.google.com/go/translate/apiv3/translatepb"
)

// ==========================================
// 🌐 OMNI TRANSLATE — MULTI-LANGUAGE ENGINE
// ==========================================

type TranslateBridge struct {
	projectID string
	location  string
}

func NewTranslateBridge(projectID, location string) *TranslateBridge {
	return &TranslateBridge{projectID: projectID, location: location}
}

func (t *TranslateBridge) parentPath() string {
	return fmt.Sprintf("projects/%s/locations/%s", t.projectID, t.location)
}

func (t *TranslateBridge) TranslateText(ctx context.Context, texts []string, targetLang, sourceLang string) ([]string, error) {
	client, err := translate.NewTranslationClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_TRANSLATE_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &translatepb.TranslateTextRequest{
		Parent:             t.parentPath(),
		Contents:           texts,
		TargetLanguageCode: targetLang,
		MimeType:           "text/plain",
	}
	if sourceLang != "" {
		req.SourceLanguageCode = sourceLang
	}

	resp, err := client.TranslateText(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("OMNI_TRANSLATE_ERROR: gagal terjemahkan: %v", err)
	}

	var results []string
	for _, tr := range resp.Translations {
		results = append(results, tr.TranslatedText)
	}
	log.Printf("🌐 [OMNI TRANSLATE] %d teks diterjemahkan ke '%s'", len(results), targetLang)
	return results, nil
}

func (t *TranslateBridge) DetectLanguage(ctx context.Context, text string) (string, float32, error) {
	client, err := translate.NewTranslationClient(ctx)
	if err != nil {
		return "", 0, fmt.Errorf("OMNI_TRANSLATE_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	resp, err := client.DetectLanguage(ctx, &translatepb.DetectLanguageRequest{
		Parent:   t.parentPath(),
		Source:   &translatepb.DetectLanguageRequest_Content{Content: text},
		MimeType: "text/plain",
	})
	if err != nil {
		return "", 0, fmt.Errorf("OMNI_TRANSLATE_ERROR: gagal deteksi bahasa: %v", err)
	}

	if len(resp.Languages) == 0 {
		return "unknown", 0, nil
	}
	lang := resp.Languages[0]
	log.Printf("🌐 [OMNI TRANSLATE] Bahasa terdeteksi: %s (%.1f%%)", lang.LanguageCode, lang.Confidence*100)
	return lang.LanguageCode, lang.Confidence, nil
}
