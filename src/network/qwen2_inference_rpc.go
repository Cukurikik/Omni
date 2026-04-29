package network

import (
    "context"
    "fmt"
)

type Qwen2Service struct{}

func (s *Qwen2Service) Forward(ctx context.Context, input []byte) ([]byte, error) {
    if len(input) == 0 {
        return nil, fmt.Errorf("empty input for Qwen2")
    }
    return []byte("qwen2 output"), nil
}
