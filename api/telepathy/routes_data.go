package telepathy

import (
	"context"

	"omnitools/cloud_apis"
)

// RoutesData menangani BigQuery, Spanner, Cloud SQL, Firestore, Bigtable, Redis, AlloyDB
func RoutesData(ctx context.Context, method string, args map[string]interface{}, ok func(interface{}) OmniResponse, fail func(error) OmniResponse) (OmniResponse, bool) {
	projectId, _ := args["projectId"].(string)

	switch method {

	// ── CLOUD SQL ────────────────────────────────────────────────────
	case "gcp::CloudSQL::ListInstances":
		bridge := cloud_apis.NewCloudSQLBridge(projectId)
		res, err := bridge.ListInstances(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::CloudSQL::GetInstance":
		name, _ := args["instanceName"].(string)
		bridge := cloud_apis.NewCloudSQLBridge(projectId)
		res, err := bridge.GetInstance(ctx, name)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::CloudSQL::ListDatabases":
		name, _ := args["instanceName"].(string)
		bridge := cloud_apis.NewCloudSQLBridge(projectId)
		res, err := bridge.ListDatabases(ctx, name)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::CloudSQL::CreateInstance":
		name, _ := args["instanceName"].(string)
		dbVer, _ := args["dbVersion"].(string)
		tier, _ := args["tier"].(string)
		region, _ := args["region"].(string)
		res, err := cloud_apis.NewCloudSQLBridge(projectId).CreateInstance(ctx, name, dbVer, tier, region)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::CloudSQL::DeleteInstance":
		name, _ := args["instanceName"].(string)
		res, err := cloud_apis.NewCloudSQLBridge(projectId).DeleteInstance(ctx, name)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::CloudSQL::RestartInstance":
		name, _ := args["instanceName"].(string)
		res, err := cloud_apis.NewCloudSQLBridge(projectId).RestartInstance(ctx, name)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── SPANNER ─────────────────────────────────────────────────────
	case "gcp::Spanner::ExecuteQuery":
		instanceId, _ := args["instanceId"].(string)
		databaseId, _ := args["databaseId"].(string)
		sql, _ := args["sql"].(string)
		bridge := cloud_apis.NewSpannerBridge(projectId, instanceId, databaseId)
		res, err := bridge.ExecuteQuery(ctx, sql, nil)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── REDIS ───────────────────────────────────────────────────────
	case "gcp::Redis::GetInstanceInfo":
		location, _ := args["location"].(string)
		instance, _ := args["instance"].(string)
		bridge := cloud_apis.NewRedisBridge(projectId, location, instance)
		res, err := bridge.GetInstanceInfo(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── RESOURCE MANAGER ────────────────────────────────────────────
	case "gcp::ResourceManager::GetProject":
		bridge := cloud_apis.NewResourceManagerBridge(projectId)
		res, err := bridge.GetProject(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::ResourceManager::SearchProjects":
		query, _ := args["query"].(string)
		bridge := cloud_apis.NewResourceManagerBridge(projectId)
		res, err := bridge.SearchProjects(ctx, query)
		if err != nil { return fail(err), true }
		return ok(res), true
	}

	return OmniResponse{}, false
}
