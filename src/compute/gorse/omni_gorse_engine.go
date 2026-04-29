// OMNI FRAMEWORK: BATCH 1 SEMESTER 14
// ENGINE: OMNI GORSE RECOMMENDER ENGINE
// DOMAIN: COMPUTE / MACHINE LEARNING (GO)
// ZERO MOCK - PRODUCTION READY
// ==========================================

package gorse

import (
	"context"
	"fmt"
	"math"
	"sync"
	"sync/atomic"
)

// GorseError represents domain errors for recommender.
type GorseError struct {
	Code    string
	Message string
	Err     error
}

func (e *GorseError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("GorseError[%s]: %s (%v)", e.Code, e.Message, e.Err)
	}
	return fmt.Sprintf("GorseError[%s]: %s", e.Code, e.Message)
}

// Result is the standard OMNI monadic result.
type GorseResult[T any] struct {
	Value T
	Err   error
}

// UserItemRating represents an explicit or implicit rating.
type UserItemRating struct {
	UserID    string
	ItemID    string
	Score     float64
	Timestamp int64
}

// OmniGorseEngine provides collaborative filtering recommendation.
type OmniGorseEngine struct {
	mu             sync.RWMutex
	latentDim      int
	learningRate   float64
	regularization float64
	userFactors    map[string][]float64
	itemFactors    map[string][]float64
	globalMean     float64
	userBiases     map[string]float64
	itemBiases     map[string]float64
	
	// Metrics
	totalRatings   atomic.Int64
	trainEpochs    atomic.Int64
	isTrained      atomic.Bool
}

// NewOmniGorseEngine initializes the recommender with given hyperparameters.
func NewOmniGorseEngine(latentDim int, lr float64, reg float64) *OmniGorseEngine {
	return &OmniGorseEngine{
		latentDim:      latentDim,
		learningRate:   lr,
		regularization: reg,
		userFactors:    make(map[string][]float64),
		itemFactors:    make(map[string][]float64),
		userBiases:     make(map[string]float64),
		itemBiases:     make(map[string]float64),
	}
}

// IngestData accepts raw interaction data for training.
func (e *OmniGorseEngine) IngestData(ratings []UserItemRating) GorseResult[bool] {
	e.mu.Lock()
	defer e.mu.Unlock()

	if len(ratings) == 0 {
		return GorseResult[bool]{Err: &GorseError{Code: "EMPTY_DATA", Message: "Cannot ingest empty rating array"}}
	}

	var sum float64
	for _, r := range ratings {
		sum += r.Score
		// Initialize factors if not present
		if _, exists := e.userFactors[r.UserID]; !exists {
			e.userFactors[r.UserID] = make([]float64, e.latentDim)
			for i := 0; i < e.latentDim; i++ {
				e.userFactors[r.UserID][i] = 0.1 // small init
			}
		}
		if _, exists := e.itemFactors[r.ItemID]; !exists {
			e.itemFactors[r.ItemID] = make([]float64, e.latentDim)
			for i := 0; i < e.latentDim; i++ {
				e.itemFactors[r.ItemID][i] = 0.1 // small init
			}
		}
	}
	e.globalMean = sum / float64(len(ratings))
	e.totalRatings.Add(int64(len(ratings)))

	return GorseResult[bool]{Value: true}
}

// Train executes Stochastic Gradient Descent (SGD) for matrix factorization.
func (e *OmniGorseEngine) Train(ctx context.Context, ratings []UserItemRating, epochs int) GorseResult[float64] {
	e.mu.Lock()
	defer e.mu.Unlock()

	if len(e.userFactors) == 0 || len(e.itemFactors) == 0 {
		return GorseResult[float64]{Err: &GorseError{Code: "UNTRAINED", Message: "No data ingested yet"}}
	}

	var finalRMSE float64

	for ep := 0; ep < epochs; ep++ {
		// Check context cancellation
		select {
		case <-ctx.Done():
			return GorseResult[float64]{Err: ctx.Err()}
		default:
		}

		var sqErrSum float64
		for _, r := range ratings {
			pred := e.predictInternal(r.UserID, r.ItemID)
			err := r.Score - pred
			sqErrSum += err * err

			// Update biases
			e.userBiases[r.UserID] += e.learningRate * (err - e.regularization*e.userBiases[r.UserID])
			e.itemBiases[r.ItemID] += e.learningRate * (err - e.regularization*e.itemBiases[r.ItemID])

			// Update latent factors
			for i := 0; i < e.latentDim; i++ {
				uf := e.userFactors[r.UserID][i]
				itf := e.itemFactors[r.ItemID][i]

				e.userFactors[r.UserID][i] += e.learningRate * (err*itf - e.regularization*uf)
				e.itemFactors[r.ItemID][i] += e.learningRate * (err*uf - e.regularization*itf)
			}
		}
		
		finalRMSE = math.Sqrt(sqErrSum / float64(len(ratings)))
		e.trainEpochs.Add(1)
	}

	e.isTrained.Store(true)
	return GorseResult[float64]{Value: finalRMSE}
}

// predictInternal computes the predicted score (no mutex lock, assumes caller has lock).
func (e *OmniGorseEngine) predictInternal(userID, itemID string) float64 {
	uBias := e.userBiases[userID]
	iBias := e.itemBiases[itemID]
	
	pred := e.globalMean + uBias + iBias
	
	uFactors, hasU := e.userFactors[userID]
	iFactors, hasI := e.itemFactors[itemID]
	
	if hasU && hasI {
		for i := 0; i < e.latentDim; i++ {
			pred += uFactors[i] * iFactors[i]
		}
	}
	return pred
}

// Predict estimates the rating a user would give an item.
func (e *OmniGorseEngine) Predict(userID, itemID string) GorseResult[float64] {
	if !e.isTrained.Load() {
		return GorseResult[float64]{Err: &GorseError{Code: "UNTRAINED", Message: "Engine must be trained first"}}
	}

	e.mu.RLock()
	defer e.mu.RUnlock()

	return GorseResult[float64]{Value: e.predictInternal(userID, itemID)}
}

// Recommend returns the top N items for a user. O(Items * LatentDim).
func (e *OmniGorseEngine) Recommend(userID string, topN int) GorseResult[[]string] {
	if !e.isTrained.Load() {
		return GorseResult[[]string]{Err: &GorseError{Code: "UNTRAINED", Message: "Engine must be trained first"}}
	}

	e.mu.RLock()
	defer e.mu.RUnlock()

	type itemScore struct {
		id    string
		score float64
	}

	var scores []itemScore
	for itemID := range e.itemFactors {
		scores = append(scores, itemScore{
			id:    itemID,
			score: e.predictInternal(userID, itemID),
		})
	}

	// Simple selection sort for Top-N (optimized for small N compared to len(items))
	// In a real DB this would use an inverted index or FAISS.
	if topN > len(scores) {
		topN = len(scores)
	}
	
	for i := 0; i < topN; i++ {
		maxIdx := i
		for j := i + 1; j < len(scores); j++ {
			if scores[j].score > scores[maxIdx].score {
				maxIdx = j
			}
		}
		scores[i], scores[maxIdx] = scores[maxIdx], scores[i]
	}

	result := make([]string, topN)
	for i := 0; i < topN; i++ {
		result[i] = scores[i].id
	}

	return GorseResult[[]string]{Value: result}
}

// Diagnostics returns system state metrics.
func (e *OmniGorseEngine) Diagnostics() map[string]interface{} {
	e.mu.RLock()
	defer e.mu.RUnlock()

	return map[string]interface{}{
		"engine":        "OmniGorseEngine",
		"version":       "1.0.0-production",
		"latent_dim":    e.latentDim,
		"total_users":   len(e.userFactors),
		"total_items":   len(e.itemFactors),
		"total_ratings": e.totalRatings.Load(),
		"train_epochs":  e.trainEpochs.Load(),
		"is_trained":    e.isTrained.Load(),
		"global_mean":   e.globalMean,
		"status":        "operational",
	}
}
