package cloud_apis

import (
	"context"
	"fmt"
	"log"

	documentai "cloud.google.com/go/documentai/apiv1"
	"cloud.google.com/go/documentai/apiv1/documentaipb"
)

// ==========================================
// 📄 OMNI DOCUMENT AI — INTELLIGENT DOCUMENT PROCESSING
// ==========================================

type DocumentAIBridge struct {
	projectID   string
	location    string
	processorID string
}

func NewDocumentAIBridge(projectID, location, processorID string) *DocumentAIBridge {
	return &DocumentAIBridge{projectID: projectID, location: location, processorID: processorID}
}

func (d *DocumentAIBridge) processorPath() string {
	return fmt.Sprintf("projects/%s/locations/%s/processors/%s", d.projectID, d.location, d.processorID)
}

func (d *DocumentAIBridge) ProcessDocument(ctx context.Context, content []byte, mimeType string) (*documentaipb.Document, error) {
	client, err := documentai.NewDocumentProcessorClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_DOCAI_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	resp, err := client.ProcessDocument(ctx, &documentaipb.ProcessRequest{
		Name: d.processorPath(),
		Source: &documentaipb.ProcessRequest_RawDocument{
			RawDocument: &documentaipb.RawDocument{Content: content, MimeType: mimeType},
		},
	})
	if err != nil {
		return nil, fmt.Errorf("OMNI_DOCAI_ERROR: gagal proses dokumen: %v", err)
	}

	doc := resp.Document
	log.Printf("📄 [OMNI DOCAI] Dokumen diproses: %d halaman, %d entitas", len(doc.Pages), len(doc.Entities))
	return doc, nil
}
