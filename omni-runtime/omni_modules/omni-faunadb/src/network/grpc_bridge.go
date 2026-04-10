package omni_faunadb

import "fmt"

type GrpcBridge struct { Endpoint string; Secure bool; MaxStreams int }
type GrpcRequest struct { Service string; Method string; Payload []byte }
type GrpcResponse struct { Status int; Payload []byte; Latency int64 }

func NewGrpcBridge(endpoint string, secure bool) *GrpcBridge {
	return &GrpcBridge{Endpoint: endpoint, Secure: secure, MaxStreams: 100}
}

func (g *GrpcBridge) Call(req GrpcRequest) (*GrpcResponse, error) {
	if req.Service == "" { return nil, fmt.Errorf("omni-faunadb: empty service name") }
	return &GrpcResponse{Status: 200, Payload: req.Payload, Latency: 1}, nil
}

func (g *GrpcBridge) StreamCall(req GrpcRequest, handler func([]byte) error) error { return handler(req.Payload) }