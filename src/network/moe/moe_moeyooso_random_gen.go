// moe_moeyooso_random_gen.go — Network
// Layer: Network — MoeYooso Random Generator Endpoint
// Inspired by: MoeYooso-Random-Generator (Random Moe element generator)

package network_moe

import (
	"encoding/json"
	"math/rand"
	"net/http"
	"time"
)

type MoeYoosoResponse struct {
	TraitID   string `json:"trait_id"`
	TraitName string `json:"trait_name"`
	Category  string `json:"category"`
	Rarity    string `json:"rarity"`
}

// Pre-loaded in-memory dictionary for ultra-fast generation
var traits = []MoeYoosoResponse{
	{"T01", "Tsundere", "Personality", "Common"},
	{"T02", "Kemonomimi", "Appearance", "Uncommon"},
	{"T03", "Zettai Ryouiki", "Clothing", "Rare"},
	{"T04", "Ahoge", "Appearance", "Common"},
}

func init() {
	rand.Seed(time.Now().UnixNano())
}

func MoeYoosoGeneratorHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Randomly select a trait
	selected := traits[rand.Intn(len(traits))]

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(selected)
}

