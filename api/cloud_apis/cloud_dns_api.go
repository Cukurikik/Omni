package cloud_apis

import (
	"context"
	"fmt"
	"log"

	dnsapi "google.golang.org/api/dns/v1"
)

// ==========================================
// 🌍 OMNI CLOUD DNS — DOMAIN NAME SYSTEM
// ==========================================

type CloudDNSBridge struct {
	projectID string
}

func NewCloudDNSBridge(projectID string) *CloudDNSBridge {
	return &CloudDNSBridge{projectID: projectID}
}

func (d *CloudDNSBridge) ListManagedZones(ctx context.Context) ([]*dnsapi.ManagedZone, error) {
	svc, err := dnsapi.NewService(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_DNS_ERROR: gagal membuat service: %v", err)
	}

	resp, err := svc.ManagedZones.List(d.projectID).Context(ctx).Do()
	if err != nil {
		return nil, fmt.Errorf("OMNI_DNS_ERROR: gagal list zones: %v", err)
	}
	log.Printf("🌍 [OMNI DNS] Ditemukan %d managed zones", len(resp.ManagedZones))
	return resp.ManagedZones, nil
}

func (d *CloudDNSBridge) ListRecordSets(ctx context.Context, zoneName string) ([]*dnsapi.ResourceRecordSet, error) {
	svc, err := dnsapi.NewService(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_DNS_ERROR: gagal membuat service: %v", err)
	}

	resp, err := svc.ResourceRecordSets.List(d.projectID, zoneName).Context(ctx).Do()
	if err != nil {
		return nil, fmt.Errorf("OMNI_DNS_ERROR: gagal list records untuk zone '%s': %v", zoneName, err)
	}
	log.Printf("🌍 [OMNI DNS] Ditemukan %d records di zone '%s'", len(resp.Rrsets), zoneName)
	return resp.Rrsets, nil
}
