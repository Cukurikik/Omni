// @omni-layer Concurrency | @omni-source lucidrains/CALM-pytorch
// @omni-description Distributed CALM inference server in Go: manages cross-attention
// composition between anchor and augmenting LLM workers via channels.
// @omni-lang Go | @omni-batch 16 | @omni-semester 16
package calm

import (
	"fmt"
	"math"
	"sync"
)

type OmniResult struct {
	Data  interface{}
	Error error
}

type CompositionRequest struct {
	AnchorHidden  [][]float64
	AugmentHidden [][]float64
	RequestID     string
}

type CompositionResponse struct {
	Composed  [][]float64
	GateScore float64
	RequestID string
}

type CALMInferenceServer struct {
	mu        sync.RWMutex
	dModel    int
	nWorkers  int
	requests  chan CompositionRequest
	responses chan CompositionResponse
	active    bool
}

func NewCALMInferenceServer(dModel, nWorkers int) *CALMInferenceServer {
	return &CALMInferenceServer{
		dModel:    dModel,
		nWorkers:  nWorkers,
		requests:  make(chan CompositionRequest, 256),
		responses: make(chan CompositionResponse, 256),
		active:    false,
	}
}

func (s *CALMInferenceServer) crossAttend(q, k, v []float64) []float64 {
	d := len(q)
	if d == 0 {
		return nil
	}
	scale := math.Sqrt(float64(d))
	dot := 0.0
	for i := 0; i < d && i < len(k); i++ {
		dot += q[i] * k[i]
	}
	weight := math.Exp(dot / scale)
	result := make([]float64, d)
	for i := 0; i < d && i < len(v); i++ {
		result[i] = weight * v[i]
	}
	return result
}

func (s *CALMInferenceServer) compose(req CompositionRequest) CompositionResponse {
	composed := make([][]float64, len(req.AnchorHidden))
	totalGate := 0.0
	for i, anchor := range req.AnchorHidden {
		if i >= len(req.AugmentHidden) {
			composed[i] = anchor
			continue
		}
		cross := s.crossAttend(anchor, req.AugmentHidden[i], req.AugmentHidden[i])
		gateInput := 0.0
		for j := 0; j < len(anchor) && j < 8; j++ {
			gateInput += anchor[j] * cross[j]
		}
		gate := 1.0 / (1.0 + math.Exp(-gateInput))
		totalGate += gate
		fused := make([]float64, len(anchor))
		for j := range anchor {
			fused[j] = anchor[j] + gate*cross[j]
		}
		composed[i] = fused
	}
	avgGate := totalGate / math.Max(float64(len(composed)), 1)
	return CompositionResponse{Composed: composed, GateScore: avgGate, RequestID: req.RequestID}
}

func (s *CALMInferenceServer) Start() {
	s.mu.Lock()
	s.active = true
	s.mu.Unlock()
	for w := 0; w < s.nWorkers; w++ {
		go func(id int) {
			for req := range s.requests {
				resp := s.compose(req)
				s.responses <- resp
			}
		}(w)
	}
}

func (s *CALMInferenceServer) Submit(req CompositionRequest) OmniResult {
	s.mu.RLock()
	defer s.mu.RUnlock()
	if !s.active {
		return OmniResult{Error: fmt.Errorf("server not started")}
	}
	s.requests <- req
	return OmniResult{Data: "submitted"}
}
