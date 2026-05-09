// OMNI Framework - Apache Pulsar Producer (Go)
// Emits high-throughput telemetry data from inference nodes

package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/apache/pulsar-client-go/pulsar"
)

func produceTelemetry() {
	client, err := pulsar.NewClient(pulsar.ClientOptions{
		URL:               "pulsar://omni-pulsar:6650",
		OperationTimeout:  30 * time.Second,
		ConnectionTimeout: 30 * time.Second,
	})
	if err != nil {
		log.Fatalf("OMNI Pulsar: Could not instantiate Pulsar client: %v", err)
	}
	defer client.Close()

	producer, err := client.CreateProducer(pulsar.ProducerOptions{
		Topic: "persistent://omni/telemetry/inference_metrics",
	})
	if err != nil {
		log.Fatalf("OMNI Pulsar: Could not instantiate Pulsar producer: %v", err)
	}
	defer producer.Close()

	ctx := context.Background()

	// Simulate emitting 5 telemetry events
	for i := 0; i < 5; i++ {
		payload := fmt.Sprintf(`{"node_id": "gpu-worker-1", "gpu_utilization": %d, "timestamp": "%s"}`, 85+i, time.Now().Format(time.RFC3339))

		msgId, err := producer.Send(ctx, &pulsar.ProducerMessage{
			Payload: []byte(payload),
		})

		if err != nil {
			log.Printf("OMNI Pulsar: Failed to publish message: %v", err)
		} else {
			log.Printf("OMNI Pulsar: Published message ID: %v", msgId)
		}

		time.Sleep(100 * time.Millisecond)
	}
}

func main() {
	fmt.Println("OMNI Telemetry Producer Starting...")
	produceTelemetry()
}
