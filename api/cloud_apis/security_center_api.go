package cloud_apis

import (
	"context"
	"fmt"
	"log"

	securitycenter "cloud.google.com/go/securitycenter/apiv1"
	"cloud.google.com/go/securitycenter/apiv1/securitycenterpb"
	"google.golang.org/api/iterator"
)

// ==========================================
// 🛡️ OMNI SECURITY CENTER — THREAT DETECTION & POSTURE
// ==========================================

type SecurityCenterBridge struct {
	projectID string
}

func NewSecurityCenterBridge(projectID string) *SecurityCenterBridge {
	return &SecurityCenterBridge{projectID: projectID}
}

func (s *SecurityCenterBridge) sourcePath() string {
	return fmt.Sprintf("projects/%s", s.projectID)
}

func (s *SecurityCenterBridge) ListFindings(ctx context.Context, filter string) ([]*securitycenterpb.ListFindingsResponse_ListFindingsResult, error) {
	client, err := securitycenter.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_SECCENTER_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	it := client.ListFindings(ctx, &securitycenterpb.ListFindingsRequest{
		Parent: fmt.Sprintf("%s/sources/-", s.sourcePath()),
		Filter: filter,
	})
	var findings []*securitycenterpb.ListFindingsResponse_ListFindingsResult
	count := 0
	for {
		f, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_SECCENTER_ERROR: gagal iterasi findings: %v", err)
		}
		findings = append(findings, f)
		count++
		if count >= 50 {
			break
		}
	}
	log.Printf("🛡️ [OMNI SECURITY] Ditemukan %d security findings", len(findings))
	return findings, nil
}

func (s *SecurityCenterBridge) ListSources(ctx context.Context) ([]*securitycenterpb.Source, error) {
	client, err := securitycenter.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_SECCENTER_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	it := client.ListSources(ctx, &securitycenterpb.ListSourcesRequest{Parent: s.sourcePath()})
	var sources []*securitycenterpb.Source
	for {
		src, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_SECCENTER_ERROR: gagal iterasi sources: %v", err)
		}
		sources = append(sources, src)
	}
	log.Printf("🛡️ [OMNI SECURITY] Ditemukan %d security sources", len(sources))
	return sources, nil
}
