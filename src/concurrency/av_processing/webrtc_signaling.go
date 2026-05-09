package avprocessing

import (
	"errors"
	"sync"
)

// Monadic Result
type SignalingResult[T any] struct {
	Value T
	Err   error
}

func Ok[T any](val T) SignalingResult[T]      { return SignalingResult[T]{Value: val, Err: nil} }
func Err[T any](err error) SignalingResult[T] { return SignalingResult[T]{Value: *new(T), Err: err} }
func (r SignalingResult[T]) IsSuccess() bool  { return r.Err == nil }

type SDP struct {
	Type string // offer, answer
	SDP  string
}

type ICECandidate struct {
	Candidate     string
	SDPMid        string
	SDPMLineIndex uint16
}

type SignalingServer struct {
	mu       sync.RWMutex
	offers   map[string]SDP
	answers  map[string]SDP
	iceQueue map[string][]ICECandidate
}

func NewSignalingServer() *SignalingServer {
	return &SignalingServer{
		offers:   make(map[string]SDP),
		answers:  make(map[string]SDP),
		iceQueue: make(map[string][]ICECandidate),
	}
}

func (s *SignalingServer) PostOffer(sessionID string, offer SDP) SignalingResult[bool] {
	if sessionID == "" || offer.SDP == "" {
		return Err[bool](errors.New("invalid session ID or offer"))
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	s.offers[sessionID] = offer
	return Ok(true)
}

func (s *SignalingServer) GetOffer(sessionID string) SignalingResult[SDP] {
	s.mu.RLock()
	defer s.mu.RUnlock()
	if offer, exists := s.offers[sessionID]; exists {
		return Ok(offer)
	}
	return Err[SDP](errors.New("offer not found"))
}

func (s *SignalingServer) PostAnswer(sessionID string, answer SDP) SignalingResult[bool] {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, exists := s.offers[sessionID]; !exists {
		return Err[bool](errors.New("cannot answer without offer"))
	}
	s.answers[sessionID] = answer
	return Ok(true)
}

func (s *SignalingServer) AddICECandidate(sessionID string, candidate ICECandidate) SignalingResult[bool] {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.iceQueue[sessionID] = append(s.iceQueue[sessionID], candidate)
	return Ok(true)
}
