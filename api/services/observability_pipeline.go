package services

import (
	"context"
	"fmt"
	"log"
	"time"

	"cloud.google.com/go/logging"
	"omnitools/cloud_apis"
)

// ==========================================
// 🔭 OMNI OBSERVABILITY PIPELINE (Wave 17)
// ==========================================
// Menyatukan Cloud Logging + Monitoring + Trace menjadi satu interface
// yang bisa dipanggil dari Telepathy Router atau PaaS Orchestrator.

// ObservabilityPipeline menyediakan akses terpadu ke seluruh telemetri GCP
type ObservabilityPipeline struct {
	projectID string
}

// NewObservabilityPipeline membuat pipeline baru
func NewObservabilityPipeline(projectID string) *ObservabilityPipeline {
	return &ObservabilityPipeline{projectID: projectID}
}

// EmitLog menulis log terstruktur ke Cloud Logging dengan severity dan metadata
func (o *ObservabilityPipeline) EmitLog(ctx context.Context, logId string, severity string, message string, labels map[string]string) error {
	bridge := cloud_apis.NewCloudLoggingBridge(o.projectID, logId)

	var sev logging.Severity
	switch severity {
	case "DEBUG":
		sev = logging.Debug
	case "INFO":
		sev = logging.Info
	case "WARNING":
		sev = logging.Warning
	case "ERROR":
		sev = logging.Error
	case "CRITICAL":
		sev = logging.Critical
	default:
		sev = logging.Info
	}

	err := bridge.WriteLog(ctx, sev, message, labels)
	if err != nil {
		return fmt.Errorf("omni.observability.log: %w", err)
	}
	log.Printf("🔭 [OBSERVABILITY] Log emitted: [%s] %s", severity, message)
	return nil
}

// EmitMetric menulis custom metric ke Cloud Monitoring
func (o *ObservabilityPipeline) EmitMetric(ctx context.Context, metricType string, value float64, labels map[string]string) error {
	bridge := cloud_apis.NewCloudMonitoringBridge(o.projectID)
	err := bridge.WriteCustomMetric(ctx, metricType, value, labels)
	if err != nil {
		return fmt.Errorf("omni.observability.metric: %w", err)
	}
	log.Printf("🔭 [OBSERVABILITY] Metric emitted: %s = %.2f", metricType, value)
	return nil
}

// QueryRecentLogs menarik log terbaru berdasarkan filter
func (o *ObservabilityPipeline) QueryRecentLogs(ctx context.Context, logId string, filter string, maxEntries int) (interface{}, error) {
	bridge := cloud_apis.NewCloudLoggingBridge(o.projectID, logId)
	entries, err := bridge.QueryLogs(ctx, filter, maxEntries)
	if err != nil {
		return nil, fmt.Errorf("omni.observability.query: %w", err)
	}
	log.Printf("🔭 [OBSERVABILITY] Queried %d log entries", len(entries))
	return entries, nil
}

// HealthCheck melakukan pengecekan kesehatan menyeluruh sistem OMNI
func (o *ObservabilityPipeline) HealthCheck(ctx context.Context) map[string]interface{} {
	result := map[string]interface{}{
		"timestamp": time.Now().UTC().Format(time.RFC3339),
		"project":   o.projectID,
		"status":    "HEALTHY",
	}

	// Cek Secret Manager availability
	vault, err := cloud_apis.NewSecretVault(ctx, o.projectID)
	if err != nil {
		result["secret_manager"] = "UNREACHABLE"
		result["status"] = "DEGRADED"
	} else {
		result["secret_manager"] = "OK"
		vault.Close()
	}

	// Cek VPC connectivity
	vpc, err := cloud_apis.NewVPCNetworkManager(ctx)
	if err != nil {
		result["vpc_network"] = "UNREACHABLE"
		result["status"] = "DEGRADED"
	} else {
		result["vpc_network"] = "OK"
		vpc.Close()
	}

	log.Printf("🔭 [OBSERVABILITY] Health check: %s", result["status"])
	return result
}
