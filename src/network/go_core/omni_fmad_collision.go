// Omni FM-AD Collision Detector (Go)
// Ref: TUM-AVS/FM-AD-Survey — Apache-2.0
package network_gocore

import "math"

type Point struct{ X, Y float64 }

func Distance(a, b Point) float64 { return math.Sqrt((a.X-b.X)*(a.X-b.X) + (a.Y-b.Y)*(a.Y-b.Y)) }
func CheckCollision(trajA, trajB []Point, threshold float64) (bool, int, float64) {
	for i := 0; i < len(trajA) && i < len(trajB); i++ {
		d := Distance(trajA[i], trajB[i])
		if d < threshold {
			return true, i, d
		}
	}
	return false, -1, 0
}
func ScenarioCriticality(velocities, distances []float64) float64 {
	minTTC := math.Inf(1)
	for i := range velocities {
		if i < len(distances) {
			ttc := distances[i] / math.Max(velocities[i], 0.01)
			if ttc < minTTC {
				minTTC = ttc
			}
		}
	}
	return 1.0 / (1.0 + minTTC)
}

