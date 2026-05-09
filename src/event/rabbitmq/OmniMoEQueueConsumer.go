package main

import (
	"encoding/json"
	"fmt"
	"log"

	amqp "github.com/rabbitmq/amqp091-go"
)

// OmniMoERequest defines the JSON structure of incoming queue messages
type OmniMoERequest struct {
	JobID       string  `json:"job_id"`
	Prompt      string  `json:"prompt"`
	MaxTokens   int     `json:"max_tokens"`
	Temperature float32 `json:"temperature"`
}

// OmniMoEQueueConsumer consumes async batch requests and forwards them to the SGLang Router
func main() {
	fmt.Println("OMNI Go (Event Layer): Starting RabbitMQ MoE Consumer...")

	conn, err := amqp.Dial("amqp://guest:guest@omni-rabbitmq:5672/")
	if err != nil {
		log.Fatalf("Failed to connect to RabbitMQ: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("Failed to open a channel: %v", err)
	}
	defer ch.Close()

	q, err := ch.QueueDeclare(
		"omni_moe_async_batch", // name
		true,                   // durable
		false,                  // delete when unused
		false,                  // exclusive
		false,                  // no-wait
		nil,                    // arguments
	)
	if err != nil {
		log.Fatalf("Failed to declare a queue: %v", err)
	}

	// QoS ensures fair dispatch
	err = ch.Qos(10, 0, false)
	if err != nil {
		log.Fatalf("Failed to set QoS: %v", err)
	}

	msgs, err := ch.Consume(
		q.Name, // queue
		"",     // consumer
		false,  // auto-ack (set to false for manual ack after processing)
		false,  // exclusive
		false,  // no-local
		false,  // no-wait
		nil,    // args
	)
	if err != nil {
		log.Fatalf("Failed to register a consumer: %v", err)
	}

	var forever chan struct{}

	go func() {
		for d := range msgs {
			var req OmniMoERequest
			err := json.Unmarshal(d.Body, &req)
			if err != nil {
				log.Printf("OMNI Warning: Error decoding JSON: %v", err)
				d.Nack(false, false) // Reject and discard malformed message
				continue
			}

			log.Printf("OMNI Go: Processing Job %s -> '%s'", req.JobID, req.Prompt)

			// Simulate pushing to the internal router (e.g., sglang_router.go)
			// processInference(req)

			// Acknowledge success
			d.Ack(false)
		}
	}()

	log.Printf("OMNI Go: [*] Waiting for messages. To exit press CTRL+C")
	<-forever
}
