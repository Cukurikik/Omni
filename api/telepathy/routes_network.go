package telepathy

import (
	"context"

	"omnitools/cloud_apis"
)

// RoutesNetwork menangani VPC, DNS, CDN, Cloud Armor, API Gateway, Service Directory
func RoutesNetwork(ctx context.Context, method string, args map[string]interface{}, ok func(interface{}) OmniResponse, fail func(error) OmniResponse) (OmniResponse, bool) {
	projectId, _ := args["projectId"].(string)
	location, _ := args["location"].(string)

	switch method {

	// ── VPC NETWORK ─────────────────────────────────────────────────
	case "gcp::VPC::ListNetworks":
		client, err := cloud_apis.NewVPCNetworkManager(ctx)
		if err != nil { return fail(err), true }
		defer client.Close()
		res, err := client.ListNetworks(projectId)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::VPC::GetNetwork":
		networkName, _ := args["networkName"].(string)
		client, err := cloud_apis.NewVPCNetworkManager(ctx)
		if err != nil { return fail(err), true }
		defer client.Close()
		res, err := client.GetNetwork(projectId, networkName)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── CLOUD DNS ───────────────────────────────────────────────────
	case "gcp::CloudDNS::ListManagedZones":
		bridge := cloud_apis.NewCloudDNSBridge(projectId)
		res, err := bridge.ListManagedZones(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::CloudDNS::ListRecordSets":
		zoneName, _ := args["zoneName"].(string)
		bridge := cloud_apis.NewCloudDNSBridge(projectId)
		res, err := bridge.ListRecordSets(ctx, zoneName)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── CLOUD CDN ───────────────────────────────────────────────────
	case "gcp::CloudCDN::ListBackendServices":
		bridge := cloud_apis.NewCloudCDNBridge(projectId)
		res, err := bridge.ListBackendServices(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::CloudCDN::ListURLMaps":
		bridge := cloud_apis.NewCloudCDNBridge(projectId)
		res, err := bridge.ListURLMaps(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── CLOUD ARMOR ─────────────────────────────────────────────────
	case "gcp::CloudArmor::ListPolicies":
		bridge := cloud_apis.NewCloudArmorBridge(projectId)
		res, err := bridge.ListPolicies(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::CloudArmor::DeployOMNIShield":
		bridge := cloud_apis.NewCloudArmorBridge(projectId)
		err := bridge.DeployOMNIShieldPolicy(ctx)
		if err != nil { return fail(err), true }
		return ok("OMNI Shield deployed"), true

	// ── API GATEWAY ─────────────────────────────────────────────────
	case "gcp::APIGateway::ListGateways":
		bridge := cloud_apis.NewAPIGatewayBridge(projectId, location)
		res, err := bridge.ListGateways(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── SERVICE DIRECTORY ───────────────────────────────────────────
	case "gcp::ServiceDirectory::ListNamespaces":
		bridge := cloud_apis.NewServiceDirectoryBridge(projectId, location)
		res, err := bridge.ListNamespaces(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::ServiceDirectory::ListServices":
		nsName, _ := args["namespaceName"].(string)
		bridge := cloud_apis.NewServiceDirectoryBridge(projectId, location)
		res, err := bridge.ListServices(ctx, nsName)
		if err != nil { return fail(err), true }
		return ok(res), true
	}

	return OmniResponse{}, false
}
