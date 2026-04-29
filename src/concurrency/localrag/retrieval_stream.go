package localrag

import (
	"errors"
)

type ChunkStreamer struct {
	DataStream chan string
}

func (cs *ChunkStreamer) StreamDocuments(docs []string) OmniResult {
	if len(docs) == 0 {
		return OmniResult{Value: nil, Error: errors.New("empty documents array")}
	}
	
	// Concurrent streaming of retrieved chunks to the frontend
	go func() {
		for _, doc := range docs {
			// Chunking logic
			chunkSize := 256
			for i := 0; i < len(doc); i += chunkSize {
				end := i + chunkSize
				if end > len(doc) {
					end = len(doc)
				}
				cs.DataStream <- doc[i:end]
			}
		}
		close(cs.DataStream)
	}()
	
	return OmniResult{Value: "Streaming initiated", Error: nil}
}
