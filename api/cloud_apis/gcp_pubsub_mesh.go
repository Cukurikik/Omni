package cloud_apis

import (
	"context"
	"fmt"
	"log"

	"cloud.google.com/go/pubsub"
)

// ==========================================
// 📡 CURRICULUM 6: EVENT-DRIVEN AGENT ARCHITECTURE
// ==========================================
// Memutus hubungan langsung (Synchronous). Jika satu Agen sibuk, 
// instruksi dilempar ke Pub/Sub (Event Sourcing Pattern).

type OmniEventMesh struct {
	Client *pubsub.Client
	Topic  *pubsub.Topic
}

/// Menghubungkan Neural-Net Agen dengan GCP Pub/Sub 
func EngageEventSourcing(ctx context.Context, projectID, topicName string) (*OmniEventMesh, error) {
	client, err := pubsub.NewClient(ctx, projectID)
	if err != nil {
		log.Printf("❌ [OMNI-PUBSUB] Gagal menyambung ke saraf pusat: %v", err)
		return nil, err
	}

	topic := client.Topic(topicName)
	fmt.Printf("📡 [OMNI-PUBSUB] Tulang Belakang Event-Driven (Topik: %s) Menyala.\n", topicName)

	return &OmniEventMesh{
		Client: client,
		Topic:  topic,
	}, nil
}

/// Pemancaran Sinyal Secara Asinkron (Zero-Blocking)
func (mesh *OmniEventMesh) PublishCognitiveEvent(ctx context.Context, message string) {
	res := mesh.Topic.Publish(ctx, &pubsub.Message{
		Data: []byte(message),
	})
	
	// Server tidak menunggu respon secara memblokir (Menghindari Deadlock Agen)
	go func() {
		id, err := res.Get(ctx)
		if err != nil {
			fmt.Printf("   ❌ [Gagal Pancar] Pesan gugur: %v\n", err)
			return
		}
		fmt.Printf("   --> 📨 [EVENT TERPANCAR] Konfirmasi Sinkron: ID %s\n", id)
	}()
}
