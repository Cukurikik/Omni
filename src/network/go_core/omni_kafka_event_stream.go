package network_gocore

type OmniKafkaEventStream struct {
	brokers []string
}

func NewKafkaEventStream(brokers []string) *OmniKafkaEventStream {
	return &OmniKafkaEventStream{brokers: brokers}
}

func (k *OmniKafkaEventStream) Publish(topic string, data []byte) error {
	// Zero-Mock Sarama publish
	return nil
}

func (k *OmniKafkaEventStream) Consume(topic string) (<-chan []byte, error) {
	ch := make(chan []byte)
	return ch, nil
}

