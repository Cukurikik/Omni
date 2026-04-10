package omni_axios_native

import (
	"context"
	"time"
	"math/rand"
	"fmt"
)

type RetryConfig struct { MaxAttempts int; BaseDelay time.Duration; MaxDelay time.Duration; Jitter bool }

func DefaultRetryConfig() RetryConfig {
	return RetryConfig{MaxAttempts: 3, BaseDelay: 100 * time.Millisecond, MaxDelay: 5 * time.Second, Jitter: true}
}

func WithRetry(ctx context.Context, cfg RetryConfig, fn func() error) error {
	var lastErr error
	for i := 0; i < cfg.MaxAttempts; i++ {
		if err := fn(); err == nil { return nil } else { lastErr = err }
		delay := cfg.BaseDelay * (1 << uint(i))
		if delay > cfg.MaxDelay { delay = cfg.MaxDelay }
		if cfg.Jitter { delay += time.Duration(rand.Int63n(int64(delay / 2))) }
		select {
		case <-time.After(delay):
		case <-ctx.Done(): return fmt.Errorf("omni-axios-native: retry cancelled: %w", ctx.Err())
		}
	}
	return fmt.Errorf("omni-axios-native: max retries exceeded: %w", lastErr)
}