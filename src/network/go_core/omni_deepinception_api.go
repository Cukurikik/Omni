// Omni DeepInception Defense API (Go)
package network_gocore

import "strings"

var inceptionMarkers = []string{"create a story", "imagine a world", "roleplay as", "pretend you are", "nested scenario"}
var harmfulCats = []string{"violence", "weapon", "hack", "exploit", "steal", "attack", "malware"}

func DetectInception(prompt string) (bool, float64) {
	pl := strings.ToLower(prompt)
	im := 0
	hm := 0
	for _, m := range inceptionMarkers {
		if strings.Contains(pl, m) {
			im++
		}
	}
	for _, h := range harmfulCats {
		if strings.Contains(pl, h) {
			hm++
		}
	}
	score := float64(im)*0.15 + float64(hm)*0.2
	if score > 1 {
		score = 1
	}
	return im >= 2 && hm >= 1, score
}

