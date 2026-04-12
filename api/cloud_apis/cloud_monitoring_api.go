package cloud_apis

import (
	"context"
	"fmt"
	"log"
	"time"

	monitoring "cloud.google.com/go/monitoring/apiv3/v2"
	"cloud.google.com/go/monitoring/apiv3/v2/monitoringpb"
	"google.golang.org/api/iterator"
	metricpb "google.golang.org/genproto/googleapis/api/metric"
	monitoredrespb "google.golang.org/genproto/googleapis/api/monitoredres"
	"google.golang.org/protobuf/types/known/timestamppb"
)

// ==========================================
// 📊 OMNI CLOUD MONITORING — METRICS & ALERTING
// ==========================================
// Cloud Monitoring menyediakan observability platform.
//
// OMNI Framework menggunakan Cloud Monitoring untuk:
//   - Custom metrics (latency, throughput, error rate)
//   - Uptime checks untuk SLA monitoring (99.99%)
//   - Alert policies untuk incident response
//   - Dashboard untuk OMNI Cloud operator
//
// Target ARR: bagian dari Enterprise SLA tier
// ==========================================

// CloudMonitoringBridge menyediakan akses ke Cloud Monitoring
type CloudMonitoringBridge struct {
	projectID string
}

// NewCloudMonitoringBridge membuat bridge baru ke Cloud Monitoring
func NewCloudMonitoringBridge(projectID string) *CloudMonitoringBridge {
	return &CloudMonitoringBridge{
		projectID: projectID,
	}
}

// projectPath menghasilkan fully-qualified project path
func (m *CloudMonitoringBridge) projectPath() string {
	return fmt.Sprintf("projects/%s", m.projectID)
}

// WriteCustomMetric menulis custom metric time series ke Cloud Monitoring
func (m *CloudMonitoringBridge) WriteCustomMetric(ctx context.Context, metricType string, value float64, labels map[string]string) error {
	client, err := monitoring.NewMetricClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_MONITORING_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	now := timestamppb.Now()

	req := &monitoringpb.CreateTimeSeriesRequest{
		Name: m.projectPath(),
		TimeSeries: []*monitoringpb.TimeSeries{
			{
				Metric: &metricpb.Metric{
					Type:   fmt.Sprintf("custom.googleapis.com/omni/%s", metricType),
					Labels: labels,
				},
				Resource: &monitoredrespb.MonitoredResource{
					Type: "global",
					Labels: map[string]string{
						"project_id": m.projectID,
					},
				},
				Points: []*monitoringpb.Point{
					{
						Interval: &monitoringpb.TimeInterval{
							EndTime: now,
						},
						Value: &monitoringpb.TypedValue{
							Value: &monitoringpb.TypedValue_DoubleValue{
								DoubleValue: value,
							},
						},
					},
				},
			},
		},
	}

	err = client.CreateTimeSeries(ctx, req)
	if err != nil {
		return fmt.Errorf("OMNI_MONITORING_ERROR: gagal menulis metric '%s': %v", metricType, err)
	}

	log.Printf("📊 [OMNI MONITORING] Custom metric ditulis: omni/%s = %.2f", metricType, value)
	return nil
}

// ListTimeSeries membaca time series data berdasarkan filter
func (m *CloudMonitoringBridge) ListTimeSeries(ctx context.Context, metricFilter string, startTime, endTime time.Time) ([]*monitoringpb.TimeSeries, error) {
	client, err := monitoring.NewMetricClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_MONITORING_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &monitoringpb.ListTimeSeriesRequest{
		Name:   m.projectPath(),
		Filter: metricFilter,
		Interval: &monitoringpb.TimeInterval{
			StartTime: timestamppb.New(startTime),
			EndTime:   timestamppb.New(endTime),
		},
	}

	it := client.ListTimeSeries(ctx, req)
	var series []*monitoringpb.TimeSeries
	for {
		ts, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_MONITORING_ERROR: gagal iterasi time series: %v", err)
		}
		series = append(series, ts)
	}

	log.Printf("📊 [OMNI MONITORING] Ditemukan %d time series untuk filter '%s'", len(series), metricFilter)
	return series, nil
}
