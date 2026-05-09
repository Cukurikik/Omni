package omni_lottie_web_test

import (
    "bytes"
    "testing"
    "omni/modules/omni-lottie-web/src/network"
)

func TestProtocolEncodeDecode(t *testing.T) {
    p := network.NewProtocolHandler(1024)
    msg := &network.Message{Type: network.MsgRequest, Payload: []byte("hello")}
    encoded, _ := p.Encode(msg)
    decoded, _ := p.Decode(bytes.NewReader(encoded))
    if decoded.Type != network.MsgRequest { t.Fatal("type mismatch") }
}
