package telepathy

import (
	"context"
	"fmt"

	"omnitools/services"
)

// ==========================================
// 🔧 OMNI ORCHESTRATOR ROUTES (Wave 21)
// ==========================================
// Wires Observability, CICD, and DataPipeline orchestrators
// to the Telepathy Router so they're callable via HTTP.

const defaultProjectID = "omni-tool-9c48b"
const defaultLocation = "asia-southeast1"

// RoutesOrchestrators dispatches orchestrator-level operations
func RoutesOrchestrators(ctx context.Context, method string, args map[string]interface{}, ok func(interface{}) OmniResponse, fail func(error) OmniResponse) (OmniResponse, bool) {

	// Helper to extract string args with defaults
	str := func(key, fallback string) string {
		if v, exists := args[key].(string); exists && v != "" {
			return v
		}
		return fallback
	}

	switch method {

	// ── OBSERVABILITY PIPELINE ────────────────────────────────────

	case "omni::observability::EmitLog":
		logId := str("logId", "omni-gateway")
		severity := str("severity", "INFO")
		message := str("message", "")
		labels, _ := args["labels"].(map[string]interface{})
		strLabels := make(map[string]string)
		for k, v := range labels {
			strLabels[k] = fmt.Sprintf("%v", v)
		}
		pipe := services.NewObservabilityPipeline(str("projectId", defaultProjectID))
		err := pipe.EmitLog(ctx, logId, severity, message, strLabels)
		if err != nil {
			return fail(err), true
		}
		return ok("Log emitted"), true

	case "omni::observability::EmitMetric":
		metricType := str("metricType", "")
		value, _ := args["value"].(float64)
		labels, _ := args["labels"].(map[string]interface{})
		strLabels := make(map[string]string)
		for k, v := range labels {
			strLabels[k] = fmt.Sprintf("%v", v)
		}
		pipe := services.NewObservabilityPipeline(str("projectId", defaultProjectID))
		err := pipe.EmitMetric(ctx, metricType, value, strLabels)
		if err != nil {
			return fail(err), true
		}
		return ok("Metric emitted"), true

	case "omni::observability::QueryLogs":
		logId := str("logId", "omni-gateway")
		filter := str("filter", "")
		maxEntries := 100
		if v, exists := args["maxEntries"].(float64); exists {
			maxEntries = int(v)
		}
		pipe := services.NewObservabilityPipeline(str("projectId", defaultProjectID))
		entries, err := pipe.QueryRecentLogs(ctx, logId, filter, maxEntries)
		if err != nil {
			return fail(err), true
		}
		return ok(entries), true

	case "omni::observability::HealthCheck":
		pipe := services.NewObservabilityPipeline(str("projectId", defaultProjectID))
		result := pipe.HealthCheck(ctx)
		return ok(result), true

	// ── CI/CD ORCHESTRATOR ───────────────────────────────────────

	case "omni::cicd::ListBuilds":
		orch := services.NewCICDOrchestrator(str("projectId", defaultProjectID), str("location", defaultLocation))
		builds, err := orch.ListRecentBuilds(ctx)
		if err != nil {
			return fail(err), true
		}
		return ok(builds), true

	case "omni::cicd::ListArtifacts":
		orch := services.NewCICDOrchestrator(str("projectId", defaultProjectID), str("location", defaultLocation))
		artifacts, err := orch.ListArtifacts(ctx)
		if err != nil {
			return fail(err), true
		}
		return ok(artifacts), true

	case "omni::cicd::Deploy":
		serviceName := str("serviceName", "")
		orch := services.NewCICDOrchestrator(str("projectId", defaultProjectID), str("location", defaultLocation))
		result, err := orch.DeployToCloudRun(ctx, serviceName)
		if err != nil {
			return fail(err), true
		}
		return ok(result), true

	case "omni::cicd::PipelineStatus":
		orch := services.NewCICDOrchestrator(str("projectId", defaultProjectID), str("location", defaultLocation))
		status := orch.FullPipelineStatus(ctx)
		return ok(status), true

	// ── DATA ANALYTICS PIPELINE ──────────────────────────────────

	case "omni::data::RunQuery":
		sql := str("sql", "")
		pipe := services.NewDataPipeline(str("projectId", defaultProjectID), str("location", defaultLocation))
		results, err := pipe.RunAnalyticsQuery(ctx, sql)
		if err != nil {
			return fail(err), true
		}
		return ok(results), true

	case "omni::data::ListDatasets":
		pipe := services.NewDataPipeline(str("projectId", defaultProjectID), str("location", defaultLocation))
		datasets, err := pipe.ListDatasets(ctx)
		if err != nil {
			return fail(err), true
		}
		return ok(datasets), true

	case "omni::data::PublishEvent":
		topicName := str("topicName", "")
		payload := str("payload", "")
		pipe := services.NewDataPipeline(str("projectId", defaultProjectID), str("location", defaultLocation))
		msgId, err := pipe.PublishEvent(topicName, []byte(payload))
		if err != nil {
			return fail(err), true
		}
		return ok(map[string]string{"messageId": msgId}), true

	case "omni::data::PipelineStatus":
		pipe := services.NewDataPipeline(str("projectId", defaultProjectID), str("location", defaultLocation))
		status := pipe.PipelineStatus(ctx)
		return ok(status), true
	}

	return OmniResponse{}, false
}
