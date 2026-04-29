// Omni AIMirror Parallel Download Service (Go)
// Ref: livehl/aimirror — MIT
package go_core

import "math"

type ChunkRange struct {
	ChunkID int   `json:"chunk_id"`
	Start   int64 `json:"start"`
	End     int64 `json:"end"`
	Size    int64 `json:"size"`
}

func ComputeChunks(fileSize int64, nChunks int) []ChunkRange {
	chunkSize := int64(math.Ceil(float64(fileSize) / float64(nChunks)))
	chunks := make([]ChunkRange, 0, nChunks)
	for i := 0; i < nChunks; i++ {
		start := int64(i) * chunkSize
		end := start + chunkSize - 1
		if end >= fileSize { end = fileSize - 1 }
		if start > fileSize-1 { break }
		chunks = append(chunks, ChunkRange{ChunkID: i, Start: start, End: end, Size: end - start + 1})
	}
	return chunks
}

func CacheKey(registry, pkg, version string) string {
	return registry + ":" + pkg + ":" + version
}

func EstimateSpeedup(seqMs, parMs float64) float64 {
	if parMs < 0.001 { return 0 }
	return math.Round(seqMs/parMs*10) / 10
}
