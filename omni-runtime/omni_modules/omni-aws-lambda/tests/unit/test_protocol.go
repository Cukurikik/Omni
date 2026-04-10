package omni_aws_lambda_test

import (
    "bytes"
    "testing"
)

func TestProtocolEncodeDecode(t *testing.T) {
    p := NewProtocolHandler(1024)
    msg := &Message{Type: MsgRequest, Payload: []byte("hello")}
    encoded, _ := p.Encode(msg)
    decoded, _ := p.Decode(bytes.NewReader(encoded))
    if decoded.Type != MsgRequest { t.Fatal("type mismatch") }
}