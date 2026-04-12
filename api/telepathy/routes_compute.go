package telepathy

import (
	"context"

	"omnitools/cloud_apis"
)

// RoutesCompute menangani semua invokasi Compute Engine, App Engine, Cloud Run, dan GKE
func RoutesCompute(ctx context.Context, method string, args map[string]interface{}, ok func(interface{}) OmniResponse, fail func(error) OmniResponse) (OmniResponse, bool) {
	projectId, _ := args["projectId"].(string)
	zone, _ := args["zone"].(string)
	location, _ := args["location"].(string)

	switch method {

	// ── COMPUTE ENGINE ──────────────────────────────────────────────
	case "gcp::ComputeEngine::ListInstances":
		bridge := cloud_apis.NewComputeEngineBridge(projectId, zone)
		res, err := bridge.ListInstances(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::ComputeEngine::GetInstance":
		name, _ := args["instanceName"].(string)
		bridge := cloud_apis.NewComputeEngineBridge(projectId, zone)
		res, err := bridge.GetInstance(ctx, name)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::ComputeEngine::StartInstance":
		name, _ := args["instanceName"].(string)
		bridge := cloud_apis.NewComputeEngineBridge(projectId, zone)
		err := bridge.StartInstance(ctx, name)
		if err != nil { return fail(err), true }
		return ok("Instance started"), true

	case "gcp::ComputeEngine::StopInstance":
		name, _ := args["instanceName"].(string)
		bridge := cloud_apis.NewComputeEngineBridge(projectId, zone)
		err := bridge.StopInstance(ctx, name)
		if err != nil { return fail(err), true }
		return ok("Instance stopped"), true

	case "gcp::ComputeEngine::ListDisks":
		bridge := cloud_apis.NewComputeEngineBridge(projectId, zone)
		res, err := bridge.ListDisks(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::ComputeEngine::ListSnapshots":
		bridge := cloud_apis.NewComputeEngineBridge(projectId, zone)
		res, err := bridge.ListSnapshots(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::ComputeEngine::CreateSnapshot":
		diskName, _ := args["diskName"].(string)
		snapshotName, _ := args["snapshotName"].(string)
		bridge := cloud_apis.NewComputeEngineBridge(projectId, zone)
		err := bridge.CreateSnapshot(ctx, diskName, snapshotName)
		if err != nil { return fail(err), true }
		return ok("Snapshot created"), true

	// ── APP ENGINE ──────────────────────────────────────────────────
	case "gcp::AppEngine::GetApplication":
		bridge := cloud_apis.NewAppEngineBridge(projectId)
		res, err := bridge.GetApplication(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::AppEngine::ListServices":
		bridge := cloud_apis.NewAppEngineBridge(projectId)
		res, err := bridge.ListServices(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::AppEngine::ListVersions":
		serviceId, _ := args["serviceId"].(string)
		bridge := cloud_apis.NewAppEngineBridge(projectId)
		res, err := bridge.ListVersions(ctx, serviceId)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── CLOUD RUN ───────────────────────────────────────────────────
	case "gcp::CloudRun::ListServices":
		bridge := cloud_apis.NewCloudRunBridge(projectId, location)
		res, err := bridge.ListServices(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::CloudRun::GetService":
		svcName, _ := args["serviceName"].(string)
		bridge := cloud_apis.NewCloudRunBridge(projectId, location)
		res, err := bridge.GetService(ctx, svcName)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::CloudRun::DeleteService":
		svcName, _ := args["serviceName"].(string)
		bridge := cloud_apis.NewCloudRunBridge(projectId, location)
		err := bridge.DeleteService(ctx, svcName)
		if err != nil { return fail(err), true }
		return ok("Service deleted"), true

	case "gcp::CloudRun::ListRevisions":
		svcName, _ := args["serviceName"].(string)
		bridge := cloud_apis.NewCloudRunBridge(projectId, location)
		res, err := bridge.ListRevisions(ctx, svcName)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── GKE (KUBERNETES ENGINE) ─────────────────────────────────────
	case "gcp::GKE::ListClusters":
		bridge := cloud_apis.NewGKEBridge(projectId, location)
		res, err := bridge.ListClusters(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::GKE::GetCluster":
		clusterName, _ := args["clusterName"].(string)
		bridge := cloud_apis.NewGKEBridge(projectId, location)
		res, err := bridge.GetCluster(ctx, clusterName)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::GKE::ListNodePools":
		clusterName, _ := args["clusterName"].(string)
		bridge := cloud_apis.NewGKEBridge(projectId, location)
		res, err := bridge.ListNodePools(ctx, clusterName)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::GKE::DeleteCluster":
		clusterName, _ := args["clusterName"].(string)
		bridge := cloud_apis.NewGKEBridge(projectId, location)
		err := bridge.DeleteCluster(ctx, clusterName)
		if err != nil { return fail(err), true }
		return ok("Cluster deletion queued"), true

	case "gcp::GKE::GetServerConfig":
		bridge := cloud_apis.NewGKEBridge(projectId, location)
		res, err := bridge.GetServerConfig(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true
	}

	return OmniResponse{}, false
}
