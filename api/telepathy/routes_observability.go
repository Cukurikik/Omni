package telepathy

import (
	"context"
	"log"

	"omnitools/services"
)

// RoutesObservability menangani endpoint telemetri dan health-check OMNI
func RoutesObservability(ctx context.Context, method string, args map[string]interface{}, returnOk func(interface{}) OmniResponse, returnErr func(error) OmniResponse) (OmniResponse, bool) {
	switch method {

	// Dashboard real-time (goroutines, memory, latency, traces)
	case "omni::Telemetry::GetDashboard":
		telemetry := services.GetTelemetry()
		return returnOk(telemetry.GetDashboard()), true

	// Ambil N trace distributed terbaru
	case "omni::Telemetry::GetRecentTraces":
		n := 20
		if v, ok := args["limit"].(float64); ok {
			n = int(v)
		}
		telemetry := services.GetTelemetry()
		return returnOk(telemetry.GetRecentTraces(n)), true

	// Health check seluruh subsystem OMNI + GCP
	case "omni::Observability::HealthCheck":
		projectId, _ := args["projectId"].(string)
		if projectId == "" {
			projectId = "omni-cloud"
		}
		pipeline := services.NewObservabilityPipeline(projectId)
		result := pipeline.HealthCheck(ctx)
		return returnOk(result), true

	// Emit structured log ke Cloud Logging
	case "omni::Observability::EmitLog":
		projectId, _ := args["projectId"].(string)
		logId, _ := args["logId"].(string)
		severity, _ := args["severity"].(string)
		message, _ := args["message"].(string)
		labels, _ := args["labels"].(map[string]interface{})

		strLabels := make(map[string]string)
		for k, v := range labels {
			if s, ok := v.(string); ok {
				strLabels[k] = s
			}
		}

		pipeline := services.NewObservabilityPipeline(projectId)
		err := pipeline.EmitLog(ctx, logId, severity, message, strLabels)
		if err != nil {
			return returnErr(err), true
		}
		return returnOk(map[string]string{"status": "logged"}), true

	default:
		return OmniResponse{}, false
	}

	log.Println("📊 [TELEMETRY ROUTE] Permintaan observasi selesai diproses")
	return OmniResponse{}, false
}
