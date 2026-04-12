package cloud_apis

import (
	"context"
	"fmt"
	"log"

	apigateway "cloud.google.com/go/apigateway/apiv1"
	"cloud.google.com/go/apigateway/apiv1/apigatewaypb"
	"google.golang.org/api/iterator"
)

// ==========================================
// 🚪 OMNI API GATEWAY — API MANAGEMENT
// ==========================================

type APIGatewayBridge struct {
	projectID string
	location  string
}

func NewAPIGatewayBridge(projectID, location string) *APIGatewayBridge {
	return &APIGatewayBridge{projectID: projectID, location: location}
}

func (a *APIGatewayBridge) parentPath() string {
	return fmt.Sprintf("projects/%s/locations/%s", a.projectID, a.location)
}

func (a *APIGatewayBridge) ListGateways(ctx context.Context) ([]*apigatewaypb.Gateway, error) {
	client, err := apigateway.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_APIGATEWAY_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	it := client.ListGateways(ctx, &apigatewaypb.ListGatewaysRequest{Parent: a.parentPath()})
	var gateways []*apigatewaypb.Gateway
	for {
		gw, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_APIGATEWAY_ERROR: gagal iterasi: %v", err)
		}
		gateways = append(gateways, gw)
	}
	log.Printf("🚪 [OMNI API GATEWAY] Ditemukan %d gateways", len(gateways))
	return gateways, nil
}

func (a *APIGatewayBridge) ListAPIs(ctx context.Context) ([]*apigatewaypb.Api, error) {
	client, err := apigateway.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_APIGATEWAY_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	it := client.ListApis(ctx, &apigatewaypb.ListApisRequest{
		Parent: fmt.Sprintf("projects/%s/locations/global", a.projectID),
	})
	var apis []*apigatewaypb.Api
	for {
		api, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_APIGATEWAY_ERROR: gagal iterasi APIs: %v", err)
		}
		apis = append(apis, api)
	}
	log.Printf("🚪 [OMNI API GATEWAY] Ditemukan %d APIs", len(apis))
	return apis, nil
}
