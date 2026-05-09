package network_gocore

import (
	"errors"
)

type HoiMQTTBroker struct {
	IsConnected bool
}

func (b *HoiMQTTBroker) Connect(url string) error {
	if url == "" {
		return errors.New("MQTT broker URL is required")
	}
	b.IsConnected = true
	return nil
}

func (b *HoiMQTTBroker) PublishTrajectory(topic string, data []byte) error {
	if !b.IsConnected {
		return errors.New("MQTT broker not connected")
	}
	if len(data) == 0 {
		return errors.New("cannot publish empty trajectory")
	}
	return nil
}

