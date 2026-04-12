package cloud_apis

import (
	"context"
	"fmt"
	"log"

	dlp "cloud.google.com/go/dlp/apiv2"
	"cloud.google.com/go/dlp/apiv2/dlppb"
)

// ==========================================
// 🔒 OMNI DLP — DATA LOSS PREVENTION
// ==========================================

type DLPBridge struct {
	projectID string
}

func NewDLPBridge(projectID string) *DLPBridge {
	return &DLPBridge{projectID: projectID}
}

func (d *DLPBridge) InspectText(ctx context.Context, text string, infoTypes []string) ([]*dlppb.Finding, error) {
	client, err := dlp.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_DLP_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	var types []*dlppb.InfoType
	for _, t := range infoTypes {
		types = append(types, &dlppb.InfoType{Name: t})
	}

	resp, err := client.InspectContent(ctx, &dlppb.InspectContentRequest{
		Parent: fmt.Sprintf("projects/%s", d.projectID),
		Item:   &dlppb.ContentItem{DataItem: &dlppb.ContentItem_Value{Value: text}},
		InspectConfig: &dlppb.InspectConfig{
			InfoTypes:    types,
			MinLikelihood: dlppb.Likelihood_LIKELY,
		},
	})
	if err != nil {
		return nil, fmt.Errorf("OMNI_DLP_ERROR: gagal inspect text: %v", err)
	}

	findings := resp.Result.Findings
	log.Printf("🔒 [OMNI DLP] Ditemukan %d sensitive data findings", len(findings))
	return findings, nil
}

func (d *DLPBridge) DeidentifyText(ctx context.Context, text string, infoTypes []string) (string, error) {
	client, err := dlp.NewClient(ctx)
	if err != nil {
		return "", fmt.Errorf("OMNI_DLP_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	var types []*dlppb.InfoType
	for _, t := range infoTypes {
		types = append(types, &dlppb.InfoType{Name: t})
	}

	resp, err := client.DeidentifyContent(ctx, &dlppb.DeidentifyContentRequest{
		Parent: fmt.Sprintf("projects/%s", d.projectID),
		Item:   &dlppb.ContentItem{DataItem: &dlppb.ContentItem_Value{Value: text}},
		InspectConfig: &dlppb.InspectConfig{InfoTypes: types},
		DeidentifyConfig: &dlppb.DeidentifyConfig{
			Transformation: &dlppb.DeidentifyConfig_InfoTypeTransformations{
				InfoTypeTransformations: &dlppb.InfoTypeTransformations{
					Transformations: []*dlppb.InfoTypeTransformations_InfoTypeTransformation{
						{
							PrimitiveTransformation: &dlppb.PrimitiveTransformation{
								Transformation: &dlppb.PrimitiveTransformation_ReplaceWithInfoTypeConfig{},
							},
						},
					},
				},
			},
		},
	})
	if err != nil {
		return "", fmt.Errorf("OMNI_DLP_ERROR: gagal deidentify: %v", err)
	}
	log.Printf("🔒 [OMNI DLP] Teks berhasil di-deidentify")
	return resp.Item.GetValue(), nil
}
