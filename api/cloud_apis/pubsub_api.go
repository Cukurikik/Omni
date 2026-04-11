package cloud_apis

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"

	"cloud.google.com/go/pubsub"
)

// ==========================================
// ☁️ OMNI CLOUD APIs: GCP Pub/Sub Engine
// ==========================================
// Jembatan penyebaran pesan lintas Benua (Multi-region Cloud Sink)
// Berfungsi sebagai urat nadi OMNI-Swarm (Micro-SaaS) untuk Load Balancing.

type OmniPubSubClient struct {
	client *pubsub.Client
	ctx    context.Context
	mu     sync.RWMutex
	topics map[string]*pubsub.Topic
}

var PubSub *OmniPubSubClient

// InitializePubSubClient memicu Engine Global Publish/Subscribe
func InitializePubSubClient(projectID string) error {
	ctx := context.Background()
	
	// Pembentukan jalur koneksi Murni ke infrastruktur Google
	client, err := pubsub.NewClient(ctx, projectID)
	if err != nil {
		return fmt.Errorf("omni-gcp: gagal membuat klien Pub/Sub (Cek Kredensial GCP): %v", err)
	}

	PubSub = &OmniPubSubClient{
		client: client,
		ctx:    ctx,
		topics: make(map[string]*pubsub.Topic),
	}

	log.Println("✅ [CLOUD APIs] Sistem Saraf Google Cloud Pub/Sub Terkoneksi!")
	return nil
}

// PublishEventMurni mengirim pesan bytes (seperti Telemetri eBPF Sentinel atau Pesan Realtime)
// ke kluster server OMNI lain yang tersebar di wilayah/region berbeda via jaringan intra-Google.
func (ps *OmniPubSubClient) PublishEventMurni(topicName string, messagePayload []byte) (string, error) {
	if ps.client == nil {
		return "", fmt.Errorf("OMNI-PubSub uninitialized")
	}

	ps.mu.RLock()
	t, exists := ps.topics[topicName]
	ps.mu.RUnlock()

	// Caching Topik jika belum dibicarakan
	if !exists {
		ps.mu.Lock()
		t = ps.client.Topic(topicName)
		ps.topics[topicName] = t
		ps.mu.Unlock()
	}

	// Mempublish secara gRPC murni asinkronous (Batching diaktifkan otomatis oleh SDK Google)
	result := t.Publish(ps.ctx, &pubsub.Message{
		Data:        messagePayload,
		PublishTime: time.Now(),
		Attributes: map[string]string{
			"origin": "OMNI-Unikernel",
			"tier":   "enterprise",
		},
	})

	// Tunggu Server Google memvalidasi & mengembalikan ID Pesan Asli
	serverMsgID, err := result.Get(ps.ctx)
	if err != nil {
		return "", fmt.Errorf("gagal sinkronisasi dengan Google Pub/Sub Edge: %v", err)
	}

	log.Printf("📢 [API PUB/SUB] OMNI menyebar event %d byte -> G-Network (ID: %s)", len(messagePayload), serverMsgID)
	return serverMsgID, nil
}
