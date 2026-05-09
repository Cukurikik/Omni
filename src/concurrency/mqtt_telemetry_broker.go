// OMNI Engine — MQTT Telemetry Broker (Go)
// Layer: Concurrency
// Implements: Lightweight IoT message brokering logic
package concurrency

type MqttMessage struct {
	Topic   string
	Payload []byte
	QoS     int
}
