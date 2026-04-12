package cloud_apis

import (
	"context"
	"fmt"
	"log"

	vision "cloud.google.com/go/vision/apiv1"
	"cloud.google.com/go/vision/v2/apiv1/visionpb"
)

// ==========================================
// 👁️ OMNI CLOUD VISION — IMAGE INTELLIGENCE
// ==========================================

type VisionBridge struct {
	projectID string
}

func NewVisionBridge(projectID string) *VisionBridge {
	return &VisionBridge{projectID: projectID}
}

func (v *VisionBridge) DetectLabels(ctx context.Context, imageURI string) ([]*visionpb.EntityAnnotation, error) {
	client, err := vision.NewImageAnnotatorClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_VISION_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	image := &visionpb.Image{Source: &visionpb.ImageSource{ImageUri: imageURI}}
	req := &visionpb.AnnotateImageRequest{
		Image:    image,
		Features: []*visionpb.Feature{{Type: visionpb.Feature_LABEL_DETECTION, MaxResults: 10}},
	}
	batchReq := &visionpb.BatchAnnotateImagesRequest{Requests: []*visionpb.AnnotateImageRequest{req}}

	resp, err := client.BatchAnnotateImages(ctx, batchReq)
	if err != nil {
		return nil, fmt.Errorf("OMNI_VISION_ERROR: gagal deteksi label: %v", err)
	}

	labels := resp.Responses[0].LabelAnnotations
	log.Printf("👁️ [OMNI VISION] Ditemukan %d labels untuk image", len(labels))
	return labels, nil
}

func (v *VisionBridge) DetectText(ctx context.Context, imageURI string) ([]*visionpb.EntityAnnotation, error) {
	client, err := vision.NewImageAnnotatorClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_VISION_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	image := &visionpb.Image{Source: &visionpb.ImageSource{ImageUri: imageURI}}
	req := &visionpb.AnnotateImageRequest{
		Image:    image,
		Features: []*visionpb.Feature{{Type: visionpb.Feature_TEXT_DETECTION}},
	}
	batchReq := &visionpb.BatchAnnotateImagesRequest{Requests: []*visionpb.AnnotateImageRequest{req}}

	resp, err := client.BatchAnnotateImages(ctx, batchReq)
	if err != nil {
		return nil, fmt.Errorf("OMNI_VISION_ERROR: gagal deteksi teks: %v", err)
	}

	texts := resp.Responses[0].TextAnnotations
	log.Printf("👁️ [OMNI VISION] OCR selesai: %d text blocks ditemukan", len(texts))
	return texts, nil
}
