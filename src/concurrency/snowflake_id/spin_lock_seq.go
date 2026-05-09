package concurrency

import (
	"sync"
	"time"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type SpinLockSequence struct {
	lastTimestamp int64
	sequence      int64
	mu            sync.Mutex
}

func NewSpinLockSequence() *SpinLockSequence {
	return &SpinLockSequence{
		lastTimestamp: time.Now().UnixMilli(),
		sequence:      0,
	}
}

func (s *SpinLockSequence) NextSequence() OmniResult {
	s.mu.Lock()
	defer s.mu.Unlock()

	now := time.Now().UnixMilli()

	if now == s.lastTimestamp {
		s.sequence = (s.sequence + 1) & 4095
		if s.sequence == 0 {
			// Sequence exhausted for this millisecond, spin lock
			for now <= s.lastTimestamp {
				now = time.Now().UnixMilli()
			}
		}
	} else {
		s.sequence = 0
	}

	s.lastTimestamp = now

	return OmniResult{Value: s.sequence}
}
