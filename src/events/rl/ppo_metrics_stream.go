package rl

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/segmentio/kafka-go"
)

// OMNI RL - PPO Metrics Stream
// Go producer for streaming RL training metrics to OMNI Kafka Event Bus

type PPOMetric struct {
	Timestamp    int64   `json:"timestamp"`
	Episode      int     `json:"episode"`
	TotalReward  float64 `json:"total_reward"`
	ActorLoss    float64 `json:"actor_loss"`
	CriticLoss   float64 `json:"critic_loss"`
	Entropy      float64 `json:"entropy"`
	LearningRate float64 `json:"learning_rate"`
}

type MetricsProducer struct {
	writer *kafka.Writer
}

func NewMetricsProducer(brokers []string, topic string) *MetricsProducer {
	writer := &kafka.Writer{
		Addr:         kafka.TCP(brokers...),
		Topic:        topic,
		Balancer:     &kafka.LeastBytes{},
		BatchSize:    100, // Micro-batching for high throughput
		BatchTimeout: 10 * time.Millisecond,
	}

	return &MetricsProducer{writer: writer}
}

// PushMetric sends a strict JSON-encoded metric to the Kafka cluster
func (p *MetricsProducer) PushMetric(ctx context.Context, metric PPOMetric) error {
	metric.Timestamp = time.Now().UnixNano()

	bytes, err := json.Marshal(metric)
	if err != nil {
		return fmt.Errorf("failed to marshal metric: %w", err)
	}

	msg := kafka.Message{
		Key:   []byte(fmt.Sprintf("ep_%d", metric.Episode)),
		Value: bytes,
	}

	if err := p.writer.WriteMessages(ctx, msg); err != nil {
		return fmt.Errorf("failed to write metric to kafka: %w", err)
	}

	return nil
}

func (p *MetricsProducer) Close() error {
	return p.writer.Close()
}
