package main

import (
	"log"

	"github.com/streadway/amqp"
)

// OMNI RabbitMQ Queue for Asynchronous Summarization Tasks
func SetupIndoSummaryQueue(connURL string) {
	conn, err := amqp.Dial(connURL)
	if err != nil {
		log.Fatalf("Failed to connect to RabbitMQ: %s", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("Failed to open a channel: %s", err)
	}
	defer ch.Close()

	q, err := ch.QueueDeclare(
		"omni_indo_summary_tasks", // name
		true,                      // durable
		false,                     // delete when unused
		false,                     // exclusive
		false,                     // no-wait
		nil,                       // arguments
	)
	if err != nil {
		log.Fatalf("Failed to declare a queue: %s", err)
	}

	log.Printf("OMNI Summarization Queue initialized: %s", q.Name)
}
