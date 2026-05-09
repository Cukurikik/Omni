// OMNI FRAMEWORK: BATCH 1 SEMESTER 14
// ENGINE: OMNI VISTA ENGINE
// DOMAIN: COMPUTE / VISUAL SPATIAL (GO)
// ZERO MOCK - PRODUCTION READY
// ==========================================

package vista

import (
	"context"
	"fmt"
	"sync"
	"sync/atomic"
)

// VistaError defines custom error structures for spatial operations.
type VistaError struct {
	Code    string
	Message string
	Err     error
}

func (e *VistaError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("VistaError[%s]: %s (%v)", e.Code, e.Message, e.Err)
	}
	return fmt.Sprintf("VistaError[%s]: %s", e.Code, e.Message)
}

// Result is the standard OMNI monadic result.
type VistaResult[T any] struct {
	Value T
	Err   error
}

// BoundingBox represents a 2D spatial region.
type BoundingBox struct {
	XMin, YMin, XMax, YMax float64
	Label                  string
	Confidence             float64
}

// OmniVistaEngine orchestrates spatial topology computations (IoU, NMS).
type OmniVistaEngine struct {
	mu           sync.RWMutex
	framesParsed atomic.Int64
}

// NewOmniVistaEngine initializes the visual spatial engine.
func NewOmniVistaEngine() *OmniVistaEngine {
	return &OmniVistaEngine{}
}

// CalculateIoU computes the Intersection over Union between two bounding boxes.
func (e *OmniVistaEngine) CalculateIoU(boxA, boxB BoundingBox) float64 {
	xLeft := max(boxA.XMin, boxB.XMin)
	yTop := max(boxA.YMin, boxB.YMin)
	xRight := min(boxA.XMax, boxB.XMax)
	yBottom := min(boxA.YMax, boxB.YMax)

	if xRight < xLeft || yBottom < yTop {
		return 0.0
	}

	intersectionArea := (xRight - xLeft) * (yBottom - yTop)
	boxAArea := (boxA.XMax - boxA.XMin) * (boxA.YMax - boxA.YMin)
	boxBArea := (boxB.XMax - boxB.XMin) * (boxB.YMax - boxB.YMin)

	iou := intersectionArea / float64(boxAArea+boxBArea-intersectionArea)
	return iou
}

func max(a, b float64) float64 {
	if a > b {
		return a
	}
	return b
}
func min(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}

// NonMaxSuppression filters overlapping bounding boxes based on IoU threshold.
func (e *OmniVistaEngine) NonMaxSuppression(ctx context.Context, boxes []BoundingBox, iouThreshold float64) VistaResult[[]BoundingBox] {
	e.framesParsed.Add(1)

	if len(boxes) == 0 {
		return VistaResult[[]BoundingBox]{Value: []BoundingBox{}}
	}

	// Sort boxes by confidence (descending)
	for i := 0; i < len(boxes); i++ {
		for j := i + 1; j < len(boxes); j++ {
			if boxes[j].Confidence > boxes[i].Confidence {
				boxes[i], boxes[j] = boxes[j], boxes[i]
			}
		}
	}

	var keep []BoundingBox
	active := make([]bool, len(boxes))
	for i := range active {
		active[i] = true
	}

	for i := 0; i < len(boxes); i++ {
		if !active[i] {
			continue
		}

		keep = append(keep, boxes[i])

		for j := i + 1; j < len(boxes); j++ {
			if !active[j] {
				continue
			}
			iou := e.CalculateIoU(boxes[i], boxes[j])
			if iou > iouThreshold {
				active[j] = false
			}
		}
	}

	return VistaResult[[]BoundingBox]{Value: keep}
}

// Diagnostics returns system state metrics.
func (e *OmniVistaEngine) Diagnostics() map[string]interface{} {
	return map[string]interface{}{
		"engine":        "OmniVistaEngine",
		"version":       "1.0.0-production",
		"frames_parsed": e.framesParsed.Load(),
		"status":        "operational",
	}
}
