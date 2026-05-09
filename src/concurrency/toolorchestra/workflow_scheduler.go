package toolorchestra

import (
	"errors"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type WorkflowScheduler struct {
	AgentWorkers int
}

func (ws *WorkflowScheduler) OrchestrateTools(tools []string) OmniResult {
	if len(tools) == 0 {
		return OmniResult{Value: nil, Error: errors.New("empty tool list")}
	}

	var wg sync.WaitGroup
	results := make([]string, len(tools))
	var mu sync.Mutex

	semaphore := make(chan struct{}, ws.AgentWorkers)

	for i, t := range tools {
		wg.Add(1)
		go func(idx int, tool string) {
			defer wg.Done()
			semaphore <- struct{}{}

			status := "Tool Executed: " + tool

			mu.Lock()
			results[idx] = status
			mu.Unlock()

			<-semaphore
		}(i, t)
	}

	wg.Wait()
	return OmniResult{Value: results, Error: nil}
}
