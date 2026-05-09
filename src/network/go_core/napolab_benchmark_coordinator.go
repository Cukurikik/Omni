package network_gocore

import "errors"

type NapolabCoordinator struct {
	ActiveTasks map[string]bool
}

func NewNapolabCoordinator() *NapolabCoordinator {
	return &NapolabCoordinator{
		ActiveTasks: make(map[string]bool),
	}
}

func (c *NapolabCoordinator) StartBenchmark(taskId string) error {
	if taskId == "" {
		return errors.New("task ID cannot be empty")
	}
	if c.ActiveTasks[taskId] {
		return errors.New("benchmark task already running")
	}
	c.ActiveTasks[taskId] = true
	return nil
}

