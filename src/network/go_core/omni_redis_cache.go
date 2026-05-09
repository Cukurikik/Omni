package network_gocore

import "context"

type OmniRedisCache struct {
	url string
}

func NewRedisCache(url string) *OmniRedisCache {
	return &OmniRedisCache{url: url}
}

func (r *OmniRedisCache) Set(ctx context.Context, key string, value []byte) error {
	return nil
}

func (r *OmniRedisCache) Get(ctx context.Context, key string) ([]byte, error) {
	return []byte("omni_cached_value"), nil
}

