// Omni LLMeBench API Router (Go)
// Ref: qcri/LLMeBench
package go_core
import "errors"
type BenchRequest struct { Task string; Input string; Lang string; NShots int }
type BenchResult struct { Score float64; Metric string }
func ValidateRequest(req *BenchRequest) error {
	if req.Task == "" { return errors.New("OMNI_ERR: task required") }
	if req.Input == "" { return errors.New("OMNI_ERR: input required") }
	return nil
}
