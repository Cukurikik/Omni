// Omni DSBench Task Manager (Go)
// Ref: LiqiangJing/DSBench — ICLR'25
package go_core
import "errors"
type Task struct { ID string; Type string; Prediction string; GroundTruth string; Score float64 }
func EvaluateTask(t *Task) error {
	if t.Type == "" { return errors.New("OMNI_ERR: missing task type") }
	if t.Prediction == t.GroundTruth { t.Score = 1.0 } else { t.Score = 0.0 }
	return nil
}
func BatchAccuracy(tasks []Task) float64 {
	if len(tasks) == 0 { return 0 }
	s := 0.0
	for _, t := range tasks { s += t.Score }
	return s / float64(len(tasks))
}
