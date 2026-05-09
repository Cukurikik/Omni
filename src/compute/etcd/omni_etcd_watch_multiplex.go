// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Etcd Watch Multiplexer (OMNI Zero-Mock Implementation)
// Implements logical event delivery for prefix range watching.

package compute

import (
	"errors"
	"strings"
)

type EtcdResult struct {
	Value []string // Events Delivered
	Error error
}

func OkEtcdResult(val []string) EtcdResult {
	return EtcdResult{Value: val, Error: nil}
}

func ErrEtcdResult(err string) EtcdResult {
	return EtcdResult{Value: nil, Error: errors.New(err)}
}

type EtcdEvent struct {
	Key      string
	Revision int64
}

type EtcdWatcher struct {
	Prefix       string
	FromRevision int64
}

// Multiplexes an event log onto watchers based on prefix boundaries computationally
func MultiplexEvents(log []EtcdEvent, watchers []EtcdWatcher) EtcdResult {
	if len(log) == 0 {
		return ErrEtcdResult("Event log is empty.")
	}

	var deliveries []string

	for idx, watcher := range watchers {
		if watcher.FromRevision <= 0 {
			return ErrEtcdResult("Revision must be strictly positive.")
		}

		deliveredCount := 0
		for _, event := range log {
			// Delivery constraints: Event must be at or after Requested Revision,
			// AND it must match the prefix functionally.
			if event.Revision >= watcher.FromRevision {
				if strings.HasPrefix(event.Key, watcher.Prefix) {
					deliveredCount++
				}
			}
		}
		// Abstractly recording that watcher index received N events
		deliveries = append(deliveries, string(rune(idx))+" received "+string(rune(deliveredCount)))
	}

	return OkEtcdResult(deliveries)
}
