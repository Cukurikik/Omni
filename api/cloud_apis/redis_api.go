package cloud_apis

import (
	"context"
	"fmt"
	"log"

	redis "cloud.google.com/go/redis/apiv1"
	"cloud.google.com/go/redis/apiv1/redispb"
)

// ==========================================
// 🚀 OMNI MEMORYSTORE REDIS — IN-MEMORY CACHE
// ==========================================
// Memorystore menyediakan fully managed Redis untuk in-memory caching.
//
// OMNI Framework menggunakan Redis untuk:
//   - Session Storage & Caching
//   - Rate Limiting Token Buckets
//   - Real-time Leaderboards & Analytics
// ==========================================

// RedisBridge menyediakan akses ke instance Cloud Memorystore for Redis
type RedisBridge struct {
	projectID string
	location  string
	instance  string
}

// NewRedisBridge membuat instance bridge Redis baru
func NewRedisBridge(projectID, location, instance string) *RedisBridge {
	return &RedisBridge{
		projectID: projectID,
		location:  location,
		instance:  instance,
	}
}

// instancePath menghasilkan fully-qualified instance path
func (r *RedisBridge) instancePath() string {
	return fmt.Sprintf("projects/%s/locations/%s/instances/%s",
		r.projectID, r.location, r.instance)
}

// GetInstanceInfo mengambil detail instance Redis (contoh: host IP, port)
func (r *RedisBridge) GetInstanceInfo(ctx context.Context) (*redispb.Instance, error) {
	client, err := redis.NewCloudRedisClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_REDIS_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &redispb.GetInstanceRequest{
		Name: r.instancePath(),
	}

	instance, err := client.GetInstance(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("OMNI_REDIS_ERROR: gagal mengambil info instance: %v", err)
	}

	log.Printf("🚀 [OMNI REDIS] Ditemukan instance: %s pada host: %s:%d",
		instance.DisplayName, instance.Host, instance.Port)
	return instance, nil
}
