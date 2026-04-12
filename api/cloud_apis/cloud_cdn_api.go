package cloud_apis

import (
	"context"
	"fmt"
	"log"

	compute "cloud.google.com/go/compute/apiv1"
	"cloud.google.com/go/compute/apiv1/computepb"
	"google.golang.org/api/iterator"
)

// ==========================================
// ⚡ OMNI CLOUD CDN — CONTENT DELIVERY NETWORK
// ==========================================

type CloudCDNBridge struct {
	projectID string
}

func NewCloudCDNBridge(projectID string) *CloudCDNBridge {
	return &CloudCDNBridge{projectID: projectID}
}

func (c *CloudCDNBridge) ListBackendServices(ctx context.Context) ([]*computepb.BackendService, error) {
	client, err := compute.NewBackendServicesRESTClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CDN_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	it := client.List(ctx, &computepb.ListBackendServicesRequest{Project: c.projectID})
	var services []*computepb.BackendService
	for {
		svc, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_CDN_ERROR: gagal iterasi: %v", err)
		}
		services = append(services, svc)
	}
	log.Printf("⚡ [OMNI CDN] Ditemukan %d backend services", len(services))
	return services, nil
}

func (c *CloudCDNBridge) ListURLMaps(ctx context.Context) ([]*computepb.UrlMap, error) {
	client, err := compute.NewUrlMapsRESTClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CDN_ERROR: gagal membuat URL maps client: %v", err)
	}
	defer client.Close()

	it := client.List(ctx, &computepb.ListUrlMapsRequest{Project: c.projectID})
	var maps []*computepb.UrlMap
	for {
		m, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_CDN_ERROR: gagal iterasi URL maps: %v", err)
		}
		maps = append(maps, m)
	}
	log.Printf("⚡ [OMNI CDN] Ditemukan %d URL maps", len(maps))
	return maps, nil
}

// ==========================================
// EXPANSION: CACHE INVALIDATION & BACKEND BUCKETS (Wave 16)
// ==========================================

// InvalidateCache mengirim request cache purge ke URL map tertentu
func (c *CloudCDNBridge) InvalidateCache(ctx context.Context, urlMapName string, path string) error {
	client, err := compute.NewUrlMapsRESTClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_CDN_ERROR: gagal membuat URL maps client: %v", err)
	}
	defer client.Close()

	cacheInvalidationRule := &computepb.CacheInvalidationRule{
		Path: &path,
	}

	op, err := client.InvalidateCache(ctx, &computepb.InvalidateCacheUrlMapRequest{
		Project:                  c.projectID,
		UrlMap:                   urlMapName,
		CacheInvalidationRuleResource: cacheInvalidationRule,
	})
	if err != nil {
		return fmt.Errorf("OMNI_CDN_ERROR: gagal invalidate cache: %v", err)
	}
	if err := op.Wait(ctx); err != nil {
		return fmt.Errorf("OMNI_CDN_ERROR: gagal menunggu invalidation: %v", err)
	}
	log.Printf("⚡ [OMNI CDN] Cache invalidated untuk path '%s' di URL map '%s'", path, urlMapName)
	return nil
}

// ListBackendBuckets mengambil daftar backend buckets (CDN origin dari GCS)
func (c *CloudCDNBridge) ListBackendBuckets(ctx context.Context) ([]*computepb.BackendBucket, error) {
	client, err := compute.NewBackendBucketsRESTClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CDN_ERROR: gagal membuat backend buckets client: %v", err)
	}
	defer client.Close()

	it := client.List(ctx, &computepb.ListBackendBucketsRequest{Project: c.projectID})
	var buckets []*computepb.BackendBucket
	for {
		b, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_CDN_ERROR: gagal iterasi backend buckets: %v", err)
		}
		buckets = append(buckets, b)
	}
	log.Printf("⚡ [OMNI CDN] Ditemukan %d backend buckets", len(buckets))
	return buckets, nil
}
