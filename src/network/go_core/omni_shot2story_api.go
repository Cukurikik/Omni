// Omni Shot2Story Video API (Go)
package network_gocore

func DetectShotBoundaries(frameDiffs []float64, threshold float64) []int {
	var boundaries []int
	for i, d := range frameDiffs {
		if d > threshold {
			boundaries = append(boundaries, i)
		}
	}
	return boundaries
}
func CaptionQuality(pred, ref string) float64 {
	pt := toSet(pred)
	rt := toSet(ref)
	tp := 0
	for w := range pt {
		if rt[w] {
			tp++
		}
	}
	p := float64(tp) / max1(len(pt))
	r := float64(tp) / max1(len(rt))
	if p+r == 0 {
		return 0
	}
	return 2 * p * r / (p + r)
}
func toSet(s string) map[string]bool {
	m := map[string]bool{}
	for _, w := range split(s) {
		m[w] = true
	}
	return m
}
func max1(n int) float64 {
	if n < 1 {
		return 1
	}
	return float64(n)
}
func split(s string) []string {
	var r []string
	w := ""
	for _, c := range s {
		if c == ' ' {
			if w != "" {
				r = append(r, w)
				w = ""
			}
		} else {
			w += string(c)
		}
	}
	if w != "" {
		r = append(r, w)
	}
	return r
}

