package cloud_apis

import (
	"context"
	"fmt"
	"log"

	pubsub "cloud.google.com/go/pubsub"
)

// ==========================================
// 🏭 OMNI IOT/MANUFACTURING — EDGE COMPUTING & DEVICE MANAGEMENT
// ==========================================
// GCP IoT Core has been deprecated. OMNI Manufacturing uses
// Pub/Sub + Cloud Functions + Edge Computing pattern instead.
// This bridge provides the device-to-cloud telemetry pipeline
// used in manufacturing/IoT scenarios.

type ManufacturingBridge struct {
	projectID    string
	telemetryTopic string
	commandTopic   string
}

func NewManufacturingBridge(projectID, telemetryTopic, commandTopic string) *ManufacturingBridge {
	return &ManufacturingBridge{
		projectID:      projectID,
		telemetryTopic: telemetryTopic,
		commandTopic:   commandTopic,
	}
}

// PublishTelemetry sends device telemetry data to the cloud via Pub/Sub
func (m *ManufacturingBridge) PublishTelemetry(ctx context.Context, deviceID string, payload []byte, attributes map[string]string) (string, error) {
	client, err := pubsub.NewClient(ctx, m.projectID)
	if err != nil {
		return "", fmt.Errorf("OMNI_MFG_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	topic := client.Topic(m.telemetryTopic)
	attrs := map[string]string{"deviceId": deviceID, "source": "omni-manufacturing"}
	for k, v := range attributes {
		attrs[k] = v
	}

	result := topic.Publish(ctx, &pubsub.Message{
		Data:       payload,
		Attributes: attrs,
	})

	msgID, err := result.Get(ctx)
	if err != nil {
		return "", fmt.Errorf("OMNI_MFG_ERROR: gagal publish telemetry: %v", err)
	}
	log.Printf("🏭 [OMNI MFG] Telemetry dari device '%s' dikirim: msgID=%s", deviceID, msgID)
	return msgID, nil
}

// SendCommand sends a command to a device via Pub/Sub command topic
func (m *ManufacturingBridge) SendCommand(ctx context.Context, deviceID string, command []byte) (string, error) {
	client, err := pubsub.NewClient(ctx, m.projectID)
	if err != nil {
		return "", fmt.Errorf("OMNI_MFG_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	topic := client.Topic(m.commandTopic)
	result := topic.Publish(ctx, &pubsub.Message{
		Data: command,
		Attributes: map[string]string{
			"deviceId": deviceID,
			"type":     "command",
			"source":   "omni-manufacturing-control",
		},
	})

	msgID, err := result.Get(ctx)
	if err != nil {
		return "", fmt.Errorf("OMNI_MFG_ERROR: gagal kirim command: %v", err)
	}
	log.Printf("🏭 [OMNI MFG] Command ke device '%s' terkirim: msgID=%s", deviceID, msgID)
	return msgID, nil
}

// ListDeviceStates reads device state events from a subscription
func (m *ManufacturingBridge) ListDeviceStates(ctx context.Context, subscriptionID string, maxMessages int) ([]*DeviceMessage, error) {
	client, err := pubsub.NewClient(ctx, m.projectID)
	if err != nil {
		return nil, fmt.Errorf("OMNI_MFG_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	sub := client.Subscription(subscriptionID)
	sub.ReceiveSettings.MaxOutstandingMessages = maxMessages

	var messages []*DeviceMessage
	cctx, cancel := context.WithCancel(ctx)

	count := 0
	err = sub.Receive(cctx, func(_ context.Context, msg *pubsub.Message) {
		messages = append(messages, &DeviceMessage{
			DeviceID:   msg.Attributes["deviceId"],
			Data:       msg.Data,
			Attributes: msg.Attributes,
			Timestamp:  msg.PublishTime.String(),
		})
		msg.Ack()
		count++
		if count >= maxMessages {
			cancel()
		}
	})
	if err != nil && ctx.Err() == nil {
		return messages, fmt.Errorf("OMNI_MFG_ERROR: gagal receive messages: %v", err)
	}

	log.Printf("🏭 [OMNI MFG] Diterima %d device messages", len(messages))
	return messages, nil
}

type DeviceMessage struct {
	DeviceID   string
	Data       []byte
	Attributes map[string]string
	Timestamp  string
}
