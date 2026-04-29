// Omni Mistral-Haystack RAG Proxy (Go)
// Ref: anakin87/mistral-haystack
package go_core
import "errors"
type RAGRequest struct { Query string; TopK int; Pipeline string }
type RAGResponse struct { Answer string; Sources []string; Score float64 }
func ValidateRequest(req *RAGRequest) error {
	if req.Query == "" { return errors.New("OMNI_ERR: empty query") }
	if req.TopK <= 0 || req.TopK > 50 { return errors.New("OMNI_ERR: top_k out of range") }
	return nil
}
