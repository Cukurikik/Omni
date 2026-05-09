// OMNI AGENT SCOPE MESSAGE BROKER
// Domain: Multi-Agent Message Passing
// Origin: agentscope-ai/agentscope
package agents

import "errors"

type Message struct {
	Payload []byte
}

type Broker struct {
	channel chan Message
}

func NewBroker(bufferSize int) *Broker {
	return &Broker{
		channel: make(chan Message, bufferSize),
	}
}

func (b *Broker) Publish(msg Message) error {
	select {
	case b.channel <- msg:
		return nil
	default:
		return errors.New("broker channel full")
	}
}
