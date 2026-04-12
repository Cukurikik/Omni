package cloud_apis

import (
	"context"
	"fmt"
	"log"

	asset "cloud.google.com/go/asset/apiv1"
	"cloud.google.com/go/asset/apiv1/assetpb"
	"google.golang.org/api/iterator"
)

// ==========================================
// 📋 OMNI CLOUD ASSET — RESOURCE INVENTORY
// ==========================================

type CloudAssetBridge struct {
	projectID string
}

func NewCloudAssetBridge(projectID string) *CloudAssetBridge {
	return &CloudAssetBridge{projectID: projectID}
}

func (c *CloudAssetBridge) scope() string {
	return fmt.Sprintf("projects/%s", c.projectID)
}

func (c *CloudAssetBridge) ListAssets(ctx context.Context, assetTypes []string) ([]*assetpb.Asset, error) {
	client, err := asset.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_ASSET_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &assetpb.ListAssetsRequest{
		Parent:      c.scope(),
		AssetTypes:  assetTypes,
		ContentType: assetpb.ContentType_RESOURCE,
	}

	it := client.ListAssets(ctx, req)
	var assets []*assetpb.Asset
	count := 0
	for {
		a, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_ASSET_ERROR: gagal iterasi: %v", err)
		}
		assets = append(assets, a)
		count++
		if count >= 100 {
			break
		}
	}
	log.Printf("📋 [OMNI CLOUD ASSET] Ditemukan %d assets", len(assets))
	return assets, nil
}

func (c *CloudAssetBridge) SearchAllResources(ctx context.Context, query string) ([]*assetpb.ResourceSearchResult, error) {
	client, err := asset.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_ASSET_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	it := client.SearchAllResources(ctx, &assetpb.SearchAllResourcesRequest{
		Scope: c.scope(),
		Query: query,
	})
	var results []*assetpb.ResourceSearchResult
	count := 0
	for {
		r, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_ASSET_ERROR: gagal search: %v", err)
		}
		results = append(results, r)
		count++
		if count >= 50 {
			break
		}
	}
	log.Printf("📋 [OMNI CLOUD ASSET] Search '%s': %d results", query, len(results))
	return results, nil
}
