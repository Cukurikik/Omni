package rl

import (
	"encoding/json"
	"fmt"
	"time"
)

// OMNI RL: Reward Stream
// Go event producer that streams episode rewards and training metrics to a central telemetry system.
// Source: rlcode/reinforcement-learning

type EpisodeMetric struct {
	AgentID       string  `json:"agent_id"`
	EpisodeNumber int     `json:"episode"`
	TotalReward   float64 `json:"total_reward"`
	StepsTaken    int     `json:"steps"`
	Loss          float64 `json:"loss"`
	Timestamp     int64   `json:"timestamp"`
}

type RewardStream struct {
	// Represents a Kafka or Redis stream channel
	topic string
}

func NewRewardStream(topic string) *RewardStream {
	return &RewardStream{topic: topic}
}

// Emit pushes a metric event safely, ensuring training doesn't crash if telemetry fails
func (s *RewardStream) Emit(agentID string, ep int, reward float64, steps int, loss float64) {
	metric := EpisodeMetric{
		AgentID:       agentID,
		EpisodeNumber: ep,
		TotalReward:   reward,
		StepsTaken:    steps,
		Loss:          loss,
		Timestamp:     time.Now().UnixMilli(),
	}

	payload, err := json.Marshal(metric)
	if err != nil {
		fmt.Printf("[OMNI RL Telemetry] Failed to serialize metric: %v\n", err)
		return
	}

	// Simulated Network Push
	// kafkaProducer.Produce(s.topic, payload)
	fmt.Printf("[OMNI RL Telemetry - %s] %s\n", s.topic, string(payload))
}
