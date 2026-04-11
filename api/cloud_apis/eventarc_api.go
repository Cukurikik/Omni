package cloud_apis

import (
	"context"
	"fmt"
	"log"

	eventarc "cloud.google.com/go/eventarc/apiv1"
	"cloud.google.com/go/eventarc/apiv1/eventarcpb"
	"google.golang.org/api/iterator"
)

// ==========================================
// ⚡ OMNI EVENTARC — EVENT-DRIVEN ARCHITECTURE
// ==========================================
// EventArc memungkinkan routing event antar 90+ layanan GCP secara asinkron.
//
// OMNI Framework menggunakan EventArc untuk:
//   - Trigger Cloud Run / Cloud Functions
//   - Menghubungkan log audit dengan aksi otomatis
//   - Mikroservis loosely-coupled (EDA)
// ==========================================

// EventArcBridge menyediakan akses native ke EventArc Event Routing
type EventArcBridge struct {
	projectID string
	location  string
}

// NewEventArcBridge membuat bridge baru ke EventArc
func NewEventArcBridge(projectID, location string) *EventArcBridge {
	return &EventArcBridge{
		projectID: projectID,
		location:  location,
	}
}

// locationPath menghasilkan string location parent
func (e *EventArcBridge) locationPath() string {
	return fmt.Sprintf("projects/%s/locations/%s", e.projectID, e.location)
}

// ListTriggers mengambil senarai trigger eventarc pada project dan location
func (e *EventArcBridge) ListTriggers(ctx context.Context) ([]*eventarcpb.Trigger, error) {
	client, err := eventarc.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_EVENTARC_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &eventarcpb.ListTriggersRequest{
		Parent: e.locationPath(),
	}

	it := client.ListTriggers(ctx, req)
	var triggers []*eventarcpb.Trigger
	for {
		resp, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_EVENTARC_ERROR: gagal iterasi trigger: %v", err)
		}
		triggers = append(triggers, resp)
	}

	log.Printf("⚡ [OMNI EVENTARC] Berhasil melist %d triggers di %s", len(triggers), e.location)
	return triggers, nil
}
