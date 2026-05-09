package events

import (
	"context"
	"encoding/json"
	"errors"
	"time"

	"github.com/segmentio/kafka-go"
)

// OMNI Monadic Result Type for Go
type EmitResult struct {
	Partition int
	Offset    int64
	Error     error
}

type TrainingMetric struct {
	RunID     string    `json:"run_id"`
	Epoch     int       `json:"epoch"`
	Loss      float64   `json:"loss"`
	Accuracy  float64   `json:"accuracy"`
	Timestamp time.Time `json:"timestamp"`
}

type MetricsProducer struct {
	writer *kafka.Writer
}

func NewMetricsProducer(brokers []string, topic string) (*MetricsProducer, error) {
	if len(brokers) == 0 {
		return nil, errors.New("kafka brokers list cannot be empty")
	}

	writer := &kafka.Writer{
		Addr:         kafka.TCP(brokers...),
		Topic:        topic,
		Balancer:     &kafka.LeastBytes{},
		BatchSize:    100,
		BatchTimeout: 10 * time.Millisecond,
		RequiredAcks: kafka.RequireAll,
		MaxAttempts:  3,
	}

	return &MetricsProducer{writer: writer}, nil
}

func (p *MetricsProducer) Emit(ctx context.Context, metric TrainingMetric) EmitResult {
	if metric.RunID == "" {
		return EmitResult{Error: errors.New("RunID cannot be empty")}
	}
	if metric.Epoch < 0 {
		return EmitResult{Error: errors.New("Epoch cannot be negative")}
	}

	metric.Timestamp = time.Now().UTC()
	data, err := json.Marshal(metric)
	if err != nil {
		return EmitResult{Error: err}
	}

	msg := kafka.Message{
		Key:   []byte(metric.RunID),
		Value: data,
		Time:  metric.Timestamp,
	}

	err = p.writer.WriteMessages(ctx, msg)
	if err != nil {
		return EmitResult{Error: err}
	}

	return EmitResult{
		Partition: 0, // Since WriteMessages doesn't directly return partition without Reader
		Offset:    0,
		Error:     nil,
	}
}

func (p *MetricsProducer) Close() error {
	return p.writer.Close()
}
