package network_gocore

import (
	"errors"
	"sync/atomic"
)

type FluenceBalancer struct {
	Nodes []string
	index uint64
}

func (b *FluenceBalancer) NextNode() (string, error) {
	if len(b.Nodes) == 0 {
		return "", errors.New("no upstream nodes available")
	}
	idx := atomic.AddUint64(&b.index, 1)
	return b.Nodes[idx%uint64(len(b.Nodes))], nil
}

