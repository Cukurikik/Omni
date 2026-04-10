package omni_coinbase_commerce

import (
	"encoding/binary"
	"io"
	"fmt"
)

type ProtocolHandler struct {
	Version    uint8
	MaxMsgSize uint32
}

type Message struct {
	Type    uint8
	Length  uint32
	Payload []byte
}

const (
	MsgRequest  uint8 = 0x01
	MsgResponse uint8 = 0x02
	MsgError    uint8 = 0x03
	MsgPing     uint8 = 0x04
	MsgPong     uint8 = 0x05
	MsgAuth     uint8 = 0x06
)

func NewProtocolHandler(maxSize uint32) *ProtocolHandler {
	return &ProtocolHandler{Version: 1, MaxMsgSize: maxSize}
}

func (p *ProtocolHandler) Encode(msg *Message) ([]byte, error) {
	buf := make([]byte, 5+len(msg.Payload))
	buf[0] = msg.Type
	binary.BigEndian.PutUint32(buf[1:5], uint32(len(msg.Payload)))
	copy(buf[5:], msg.Payload)
	return buf, nil
}

func (p *ProtocolHandler) Decode(r io.Reader) (*Message, error) {
	header := make([]byte, 5)
	if _, err := io.ReadFull(r, header); err != nil {
		return nil, fmt.Errorf("omni-coinbase-commerce: protocol decode header: %w", err)
	}
	length := binary.BigEndian.Uint32(header[1:5])
	if length > p.MaxMsgSize {
		return nil, fmt.Errorf("omni-coinbase-commerce: message too large: %d", length)
	}
	payload := make([]byte, length)
	if _, err := io.ReadFull(r, payload); err != nil {
		return nil, fmt.Errorf("omni-coinbase-commerce: protocol decode payload: %w", err)
	}
	return &Message{Type: header[0], Length: length, Payload: payload}, nil
}