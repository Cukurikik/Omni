// Omni Langfuse Trace API (Go)
// Ref: langfuse/langfuse-docs — MIT
package go_core
import "fmt"
type Span struct { Name string; LatencyMs float64; Tokens int }
type Trace struct { ID string; Name string; Spans []Span }
func NewTrace(name string) Trace { return Trace{ID: fmt.Sprintf("tr-%d", len(name)*31337), Name: name} }
func (t *Trace) AddSpan(name string, latency float64, tokens int) { t.Spans = append(t.Spans, Span{name, latency, tokens}) }
func (t Trace) TotalCost(costPerToken float64) float64 {
	total := 0.0; for _, s := range t.Spans { total += float64(s.Tokens) * costPerToken }; return total
}
func (t Trace) AvgLatency() float64 {
	if len(t.Spans) == 0 { return 0 }
	sum := 0.0; for _, s := range t.Spans { sum += s.LatencyMs }; return sum / float64(len(t.Spans))
}
