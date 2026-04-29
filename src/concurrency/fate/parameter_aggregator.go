package fate

import (
	"errors"
	"sync"
)

type Aggregator struct {
	mu           sync.Mutex
	globalModel  []float64
	learningRate float64
}

func NewAggregator(modelSize int, lr float64) *Aggregator {
	return &Aggregator{
		globalModel:  make([]float64, modelSize),
		learningRate: lr,
	}
}

// Secure aggregation (FedAvg) over gradients
func (a *Aggregator) AggregateUpdates(updates []*ModelUpdate) error {
	if len(updates) == 0 {
		return errors.New("no updates to aggregate")
	}

	a.mu.Lock()
	defer a.mu.Unlock()

	numWorkers := float64(len(updates))
	avgGradients := make([]float64, len(a.globalModel))

	for _, update := range updates {
		if len(update.Gradients) != len(a.globalModel) {
			return errors.New("gradient dimension mismatch")
		}
		for i, g := range update.Gradients {
			avgGradients[i] += g / numWorkers
		}
	}

	// Apply aggregated gradients
	for i, avgGrad := range avgGradients {
		a.globalModel[i] -= a.learningRate * avgGrad
	}

	return nil
}
