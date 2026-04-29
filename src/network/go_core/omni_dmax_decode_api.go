// Omni DMax Decoding API (Go)
// Ref: czg1225/DMax
package go_core
import "errors"
type DecodeRequest struct { Logits [][]float64; Threshold float64; MaxTokens int }
type DecodeResponse struct { Tokens []int; NParallel int; AcceptRate float64 }
func ParallelDecode(req *DecodeRequest) (*DecodeResponse, error) {
	if len(req.Logits) == 0 { return nil, errors.New("OMNI_ERR: empty logits") }
	resp := &DecodeResponse{}
	for _, row := range req.Logits {
		if len(resp.Tokens) >= req.MaxTokens { break }
		bestIdx, bestP := 0, 0.0
		sum := 0.0
		for _, v := range row { sum += v }
		for i, v := range row {
			p := v / (sum + 1e-9)
			if p > bestP { bestP = p; bestIdx = i }
		}
		if bestP >= req.Threshold { resp.Tokens = append(resp.Tokens, bestIdx) } else { break }
	}
	resp.NParallel = len(resp.Tokens)
	return resp, nil
}
