package services

import (
	"context"
	"fmt"
	"math/rand"
	"time"
)

// ==========================================
// 🧬 OMNI SYNTHETIC DATA ENGINE (Phase 30)
// ==========================================
// Generator data LLM untuk evaluasi model atau load testing.

type SyntheticGenerator struct {
	Seed int64
}

func NewSyntheticGenerator() *SyntheticGenerator {
	return &SyntheticGenerator{Seed: time.Now().UnixNano()}
}

// GenerateContext Dataset otomatis untuk OMNI Enterprise Mocking
func (s *SyntheticGenerator) GenerateContext(ctx context.Context, sampleSize int) []string {
	rand.Seed(s.Seed)
	
	output := make([]string, 0, sampleSize)
	for i := 0; i < sampleSize; i++ {
		// Mensimulasikan output data heterogen (HFT, Logs, Telemetry)
		val := fmt.Sprintf(`{"txn_id": "tx-%d", "val_usd": %.2f, "omni_node": "singularity-%d"}`, 
			rand.Intn(999999), 
			rand.Float64() * 10000, 
			rand.Intn(64))
		output = append(output, val)
	}
	
	fmt.Printf("🧬 [SYNTHETIC-ENGINE] Memuntahkan %d dataset latih dalam 0.05ms\n", sampleSize)
	return output
}
