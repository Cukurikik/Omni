package seait

import (
	"errors"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type InstallationTask struct {
	ProjectID   string
	RepoURL     string
	Environment string
}

type InstallerPool struct {
	MaxWorkers int
}

func (ip *InstallerPool) ExecuteBatch(tasks []InstallationTask) OmniResult {
	if len(tasks) == 0 {
		return OmniResult{Value: nil, Error: errors.New("empty task list")}
	}

	var wg sync.WaitGroup
	results := make([]string, len(tasks))
	var mu sync.Mutex
	
	semaphore := make(chan struct{}, ip.MaxWorkers)

	for i, task := range tasks {
		wg.Add(1)
		go func(idx int, t InstallationTask) {
			defer wg.Done()
			semaphore <- struct{}{} // Acquire
			
			// Simulate native installation commands execution
			status := "Installed: " + t.ProjectID + " in " + t.Environment
			
			mu.Lock()
			results[idx] = status
			mu.Unlock()
			
			<-semaphore // Release
		}(i, task)
	}

	wg.Wait()
	return OmniResult{Value: results, Error: nil}
}
