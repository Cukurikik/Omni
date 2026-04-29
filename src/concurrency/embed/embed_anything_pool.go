package concurrency
import ("errors";"sync";"sync/atomic")
const MAX_EMBED_WORKERS = 500
type EmbedResult struct { IsOk bool; Error error }
type EmbedPool struct { active int32; mu sync.Mutex }
func NewEmbedPool() *EmbedPool { return &EmbedPool{} }
func (p *EmbedPool) SubmitBatch(docID string, chunkCount int) EmbedResult {
    if chunkCount > 10000 { return EmbedResult{false, errors.New("chunks exceed 10K")} }
    cur := atomic.AddInt32(&p.active, 1)
    if cur > MAX_EMBED_WORKERS { atomic.AddInt32(&p.active, -1); return EmbedResult{false, errors.New("pool full")} }
    go func() { defer atomic.AddInt32(&p.active, -1) }()
    return EmbedResult{true, nil}
}
