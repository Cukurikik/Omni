package streaming

import (
	"context"
	"encoding/json"
	"log"
	"time"

	"github.com/segmentio/kafka-go"
)

// Omni Kafka Streamer (Golang)
// Concurrency & Networking Layer
// High-throughput, non-blocking ingestion of live token streams for real-time
// transformer inference and continual learning loops.

type TokenPayload struct {
	SessionID string  `json:"session_id"`
	Tokens    []int64 `json:"tokens"`
	Timestamp int64   `json:"timestamp"`
}

type OmniKafkaIngestor struct {
	reader *kafka.Reader
	writer *kafka.Writer
}

func NewOmniKafkaIngestor(brokers []string, topicIn, topicOut, groupID string) *OmniKafkaIngestor {
	r := kafka.NewReader(kafka.ReaderConfig{
		Brokers:        brokers,
		GroupID:        groupID,
		Topic:          topicIn,
		MinBytes:       10e3, // 10KB
		MaxBytes:       10e6, // 10MB
		CommitInterval: time.Second,
	})

	w := &kafka.Writer{
		Addr:         kafka.TCP(brokers...),
		Topic:        topicOut,
		Balancer:     &kafka.LeastBytes{},
		BatchSize:    100,
		BatchTimeout: 10 * time.Millisecond,
	}

	return &OmniKafkaIngestor{reader: r, writer: w}
}

func (o *OmniKafkaIngestor) ConsumeAndForward(ctx context.Context, processFunc func(TokenPayload) ([]float32, error)) {
	for {
		m, err := o.reader.FetchMessage(ctx)
		if err != nil {
			log.Printf("Omni Kafka Fetch Error: %v\n", err)
			break
		}

		var payload TokenPayload
		if err := json.Unmarshal(m.Value, &payload); err != nil {
			log.Printf("Invalid payload: %v\n", err)
			continue
		}

		// Process via Transformer Engine (Zero-Copy passed ideally)
		embeddings, err := processFunc(payload)
		if err != nil {
			log.Printf("Inference Engine Error: %v\n", err)
			continue
		}

		// Forward Results
		resultBytes, _ := json.Marshal(map[string]interface{}{
			"session_id": payload.SessionID,
			"embeddings": embeddings,
		})

		err = o.writer.WriteMessages(ctx, kafka.Message{
			Key:   []byte(payload.SessionID),
			Value: resultBytes,
		})

		if err == nil {
			o.reader.CommitMessages(ctx, m)
		}
	}
}

func (o *OmniKafkaIngestor) Close() {
	o.reader.Close()
	o.writer.Close()
}

