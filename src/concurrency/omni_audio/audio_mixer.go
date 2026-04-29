package omni_audio

import (
	"context"
	"github.com/omni/core/result"
)

func MixAudioBuffers(ctx context.Context, a []float32, b []float32) result.Result[[]float32] {
	if len(a) != len(b) {
		return result.Err[[]float32](nil)
	}
	out := make([]float32, len(a))
	for i := range a {
		out[i] = (a[i] + b[i]) * 0.5
	}
	return result.Ok(out)
}
