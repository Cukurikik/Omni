package cloud_apis

import (
	"context"
	"fmt"

	"cloud.google.com/go/firestore"
)

// ==========================================
// 🗄️ OMNI FIRESTORE ENTERPRISE NATIVE WRAPPER
// ==========================================
// Skalabilitas global database NoSQL. Memungkinkan agen swarm menyimpan
// state asinkronus secara langsung ke Enterprise Native Mode GCP.

type OmniFirestoreCore struct {
	Client *firestore.Client
}

/// Menghubungkan Agen ke Native Datastore
/// @since 2.0.0
func InitializeFirestoreBridge(ctx context.Context, projectID string) (*OmniFirestoreCore, error) {
	client, err := firestore.NewClient(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("firestore native mode crash: %w", err)
	}
	fmt.Println("🗄️ [FIRESTORE-NATIVE] Tautan Realtime ke GCP Enterprise Datastore Terjalin.")
	return &OmniFirestoreCore{Client: client}, nil
}

/// Monadic Write Protocol OMNI Firestore
func (db *OmniFirestoreCore) WriteAgentState(ctx context.Context, collection string, docID string, data map[string]interface{}) error {
	_, err := db.Client.Collection(collection).Doc(docID).Set(ctx, data)
	if err != nil {
		return fmt.Errorf("write state rejected: %w", err)
	}
	return nil
}
