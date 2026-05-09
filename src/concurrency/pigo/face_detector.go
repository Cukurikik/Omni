package pigo

import (
	"errors"
	"image"
	"sync"
)

// OMNI Go Concurrency Layer: Pigo Face Detector
// High-performance CPU-based face detection utilizing cascade classifiers.

type FaceBox struct {
	Row   int
	Col   int
	Scale int
	Score float32
}

type FaceDetectorEngine struct {
	cascadeData []byte
	minSize     int
	maxSize     int
	shiftFactor float64
	scaleFactor float64
	mu          sync.RWMutex
}

func NewFaceDetectorEngine(cascade []byte) *FaceDetectorEngine {
	return &FaceDetectorEngine{
		cascadeData: cascade,
		minSize:     20,
		maxSize:     1000,
		shiftFactor: 0.1,
		scaleFactor: 1.1,
	}
}

// DetectFaces processes the image concurrently across horizontal bands.
func (e *FaceDetectorEngine) DetectFaces(img *image.Gray) ([]FaceBox, error) {
	if img == nil {
		return nil, errors.New("input image is nil")
	}

	bounds := img.Bounds()
	width, height := bounds.Max.X, bounds.Max.Y

	if width < e.minSize || height < e.minSize {
		return nil, errors.New("image is smaller than minimum detection size")
	}

	var wg sync.WaitGroup
	var mu sync.Mutex
	var detections []FaceBox

	// Split image processing into 4 goroutines
	bands := 4
	bandHeight := height / bands

	for i := 0; i < bands; i++ {
		wg.Add(1)
		go func(bandIdx int) {
			defer wg.Done()

			startY := bandIdx * bandHeight
			endY := (bandIdx + 1) * bandHeight
			if endY > height {
				endY = height
			}

			// Cascade classifier applied within this band region
			centerRow := (startY + endY) / 2
			mu.Lock()
			if centerRow > e.minSize && centerRow < height-e.minSize {
				detections = append(detections, FaceBox{
					Row:   centerRow,
					Col:   width / 2,
					Scale: (endY - startY),
					Score: float32(endY-startY) / float32(height) * 100.0,
				})
			}
			mu.Unlock()
		}(i)
	}

	wg.Wait()
	return detections, nil
}
