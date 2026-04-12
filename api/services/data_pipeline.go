package services

import (
	"context"
	"fmt"
	"log"

	"omnitools/cloud_apis"
)

// ==========================================
// 📊 OMNI DATA ANALYTICS PIPELINE (Wave 19)
// ==========================================
// Menyatukan BigQuery + Pub/Sub untuk data warehouse streaming.

// DataPipeline mengorkestrasikan aliran data dari ingestion ke analytics
type DataPipeline struct {
	projectID string
	location  string
}

// NewDataPipeline membuat pipeline data baru
func NewDataPipeline(projectID, location string) *DataPipeline {
	return &DataPipeline{projectID: projectID, location: location}
}

// RunAnalyticsQuery menjalankan SQL query langsung di BigQuery
func (d *DataPipeline) RunAnalyticsQuery(ctx context.Context, sql string) (interface{}, error) {
	bridge := cloud_apis.NewBigQueryBridge(d.projectID, "")
	results, err := bridge.ExecuteQuery(ctx, sql)
	if err != nil {
		return nil, fmt.Errorf("omni.data.query: %w", err)
	}
	log.Printf("📊 [DATA PIPELINE] Query executed, %d rows returned", len(results))
	return results, nil
}

// ListDatasets mengambil daftar dataset di BigQuery
func (d *DataPipeline) ListDatasets(ctx context.Context) (interface{}, error) {
	bridge := cloud_apis.NewBigQueryBridge(d.projectID, "")
	datasets, err := bridge.ListDatasets(ctx)
	if err != nil {
		return nil, fmt.Errorf("omni.data.list_datasets: %w", err)
	}
	log.Printf("📊 [DATA PIPELINE] Found %d datasets", len(datasets))
	return datasets, nil
}

// PublishEvent mengirim event ke Pub/Sub untuk ingestion ke pipeline
func (d *DataPipeline) PublishEvent(topicName string, payload []byte) (string, error) {
	if cloud_apis.PubSub == nil {
		err := cloud_apis.InitializePubSubClient(d.projectID)
		if err != nil {
			return "", fmt.Errorf("omni.data.publish: gagal init pub/sub: %w", err)
		}
	}
	if cloud_apis.PubSub != nil {
		msgId, err := cloud_apis.PubSub.PublishEventMurni(topicName, payload)
		if err != nil {
			return "", fmt.Errorf("omni.data.publish: %w", err)
		}
		log.Printf("📊 [DATA PIPELINE] Event published to '%s' (ID: %s)", topicName, msgId)
		return msgId, nil
	}
	return "", fmt.Errorf("omni.data.publish: PubSub engine not available")
}

// PipelineStatus mengembalikan status keseluruhan data pipeline
func (d *DataPipeline) PipelineStatus(ctx context.Context) map[string]interface{} {
	status := map[string]interface{}{
		"project":  d.projectID,
		"location": d.location,
	}

	// BigQuery connectivity
	datasets, err := d.ListDatasets(ctx)
	if err != nil {
		status["bigquery"] = "ERROR"
	} else {
		status["bigquery"] = "OK"
		status["datasets"] = datasets
	}

	// Pub/Sub connectivity
	if cloud_apis.PubSub != nil {
		status["pubsub"] = "OK"
	} else {
		status["pubsub"] = "NOT_INITIALIZED"
	}

	return status
}
