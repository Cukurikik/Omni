package promptpapers

import (
	"fmt"
	"context"
	"sync"
)

// OMNI PROMPTPAPERS: Concurrent Prompt Evaluation Workers
// Go worker pool for parallel execution and evaluation of LLM prompts against validation datasets.
// Source: thunlp/PromptPapers

type PromptTask struct {
	ID      string
	Prompt  string
	Input   string
	Target  string
}

type EvalResult struct {
	TaskID  string
	Score   float64
	Error   error
}

type PromptEvaluator struct {
	workerCount int
}

func NewPromptEvaluator(workers int) *PromptEvaluator {
	return &PromptEvaluator{workerCount: workers}
}

func (pe *PromptEvaluator) RunBatch(ctx context.Context, tasks []PromptTask, evalFn func(string, string) float64) []EvalResult {
	tasksChan := make(chan PromptTask, len(tasks))
	resultsChan := make(chan EvalResult, len(tasks))
	
	var wg sync.WaitGroup
	
	// Start workers
	for i := 0; i < pe.workerCount; i++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			for task := range tasksChan {
				select {
				case <-ctx.Done():
					resultsChan <- EvalResult{TaskID: task.ID, Error: ctx.Err()}
					return
				default:
					// Execute the prompt via some LLM bridge, then evaluate
					// Mocking the LLM execution for pure logical structural demonstration
					llmOutput := fmt.Sprintf("Simulated output for %s", task.Input)
					score := evalFn(llmOutput, task.Target)
					
					resultsChan <- EvalResult{
						TaskID: task.ID,
						Score:  score,
						Error:  nil,
					}
				}
			}
		}(i)
	}
	
	// Enqueue tasks
	for _, t := range tasks {
		tasksChan <- t
	}
	close(tasksChan)
	
	// Wait and close results
	go func() {
		wg.Wait()
		close(resultsChan)
	}()
	
	// Collect results
	var finalResults []EvalResult
	for res := range resultsChan {
		finalResults = append(finalResults, res)
	}
	
	return finalResults
}
