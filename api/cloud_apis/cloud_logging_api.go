package cloud_apis

import (
	"context"
	"fmt"
	"log"
	"time"

	logging "cloud.google.com/go/logging"
	logadmin "cloud.google.com/go/logging/logadmin"
	"google.golang.org/api/iterator"
)

// ==========================================
// 📋 OMNI CLOUD LOGGING — CENTRALIZED LOG MANAGEMENT
// ==========================================
// Cloud Logging mengumpulkan dan menganalisis log secara terpusat.
//
// OMNI Framework menggunakan Cloud Logging untuk:
//   - Centralized logging dari semua OMNI microservices
//   - Structured logging dengan severity levels
//   - Log-based metrics untuk alerting
//   - Audit trail untuk compliance (SOC2, ISO27001)
//
// Target ARR: bagian dari Enterprise observability tier
// ==========================================

// CloudLoggingBridge menyediakan akses ke Cloud Logging
type CloudLoggingBridge struct {
	projectID string
	logID     string
}

// NewCloudLoggingBridge membuat bridge baru ke Cloud Logging
func NewCloudLoggingBridge(projectID, logID string) *CloudLoggingBridge {
	return &CloudLoggingBridge{
		projectID: projectID,
		logID:     logID,
	}
}

// WriteLog menulis structured log entry ke Cloud Logging
func (l *CloudLoggingBridge) WriteLog(ctx context.Context, severity logging.Severity, message string, labels map[string]string) error {
	client, err := logging.NewClient(ctx, l.projectID)
	if err != nil {
		return fmt.Errorf("OMNI_LOGGING_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	logger := client.Logger(l.logID)

	logger.Log(logging.Entry{
		Severity:  severity,
		Payload:   message,
		Labels:    labels,
		Timestamp: time.Now(),
	})

	// Flush untuk memastikan log terkirim
	if err := client.Close(); err != nil {
		return fmt.Errorf("OMNI_LOGGING_ERROR: gagal flush log: %v", err)
	}

	log.Printf("📋 [OMNI LOGGING] Log ditulis: [%s] %s", severity, message)
	return nil
}

// WriteStructuredLog menulis log entry dengan JSON payload terstruktur
func (l *CloudLoggingBridge) WriteStructuredLog(ctx context.Context, severity logging.Severity, payload map[string]interface{}, labels map[string]string) error {
	client, err := logging.NewClient(ctx, l.projectID)
	if err != nil {
		return fmt.Errorf("OMNI_LOGGING_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	logger := client.Logger(l.logID)

	logger.Log(logging.Entry{
		Severity:  severity,
		Payload:   payload,
		Labels:    labels,
		Timestamp: time.Now(),
	})

	if err := client.Close(); err != nil {
		return fmt.Errorf("OMNI_LOGGING_ERROR: gagal flush structured log: %v", err)
	}

	log.Printf("📋 [OMNI LOGGING] Structured log ditulis: [%s] %d fields", severity, len(payload))
	return nil
}

// QueryLogs membaca log entries menggunakan filter query
func (l *CloudLoggingBridge) QueryLogs(ctx context.Context, filter string, maxEntries int) ([]*logging.Entry, error) {
	adminClient, err := logadmin.NewClient(ctx, l.projectID)
	if err != nil {
		return nil, fmt.Errorf("OMNI_LOGGING_ERROR: gagal membuat admin client: %v", err)
	}
	defer adminClient.Close()

	it := adminClient.Entries(ctx, logadmin.Filter(filter))
	var entries []*logging.Entry
	count := 0
	for {
		entry, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_LOGGING_ERROR: gagal iterasi log entries: %v", err)
		}
		entries = append(entries, entry)
		count++
		if count >= maxEntries {
			break
		}
	}

	log.Printf("📋 [OMNI LOGGING] Query selesai: %d entries ditemukan", len(entries))
	return entries, nil
}
