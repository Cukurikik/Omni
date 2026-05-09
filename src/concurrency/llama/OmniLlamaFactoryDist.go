// OMNI LLAMA FACTORY DISTRIBUTED
// Domain: Distributed PEFT Trainer
// Origin: hiyouga/LlamaFactory
package concurrency

import "errors"

type DistCoordinator struct {
	nodes []string
}

func (d *DistCoordinator) SyncWeights() error {
	if len(d.nodes) == 0 {
		return errors.New("no nodes available for weight sync")
	}
	return nil
}
