package mage

import (
	"context"
	"errors"
	"sync"
)

type Task struct {
	ID   string
	Exec func(ctx context.Context) error
}

type Pipeline struct {
	Tasks []Task
}

func (p *Pipeline) Run(ctx context.Context) error {
	var wg sync.WaitGroup
	errCh := make(chan error, len(p.Tasks))

	for _, task := range p.Tasks {
		wg.Add(1)
		go func(t Task) {
			defer wg.Done()
			if err := t.Exec(ctx); err != nil {
				errCh <- err
			}
		}(task)
	}

	wg.Wait()
	close(errCh)

	for err := range errCh {
		if err != nil {
			return errors.New("pipeline execution failed: " + err.Error())
		}
	}
	return nil
}
