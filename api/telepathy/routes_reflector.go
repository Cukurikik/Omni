package telepathy

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
)

// RoutesReflector adalah Universal Auto-Loader untuk 645 Paket Ekosistem Node.
func RoutesReflector(ctx context.Context, method string, args map[string]interface{}, returnOk func(interface{}) OmniResponse, returnErr func(error) OmniResponse) (OmniResponse, bool) {
	if len(method) <= 6 || method[:6] != "Node::" {
		return OmniResponse{}, false
	}

	log.Printf("📥 [UAST MULTIPLEXER] Merutekan Abstraksi '%s' menuju Node.js Reflector IPC", method)

	parts := strings.SplitN(method[6:], "::", 2)
	if len(parts) < 1 {
		return returnErr(fmt.Errorf("Format Reflector tidak valid. Gunakan Node::Package::Function")), true
	}

	packageName := parts[0]
	functionality := ""
	if len(parts) > 1 {
		functionality = parts[1]
	}

	// Ekstrak parameter kontrol Reflector jika ada
	actionValue, _ := args["omni_action"].(string)
	instanceId, _ := args["omni_instance_id"].(string)

	// Persiapkan Payload IPC menuju telepathy_reflector.mjs
	payload := map[string]interface{}{
		"package":       packageName,
		"functionality": functionality,
		"action":        actionValue,
		"instance_id":   instanceId,
		"args":          []interface{}{args},
	}

	jsonBody, err := json.Marshal(payload)
	if err != nil {
		return returnErr(fmt.Errorf("Gagal enkoding payload: %v", err)), true
	}

	resp, err := http.Post("http://127.0.0.1:3001/rpc", "application/json", bytes.NewBuffer(jsonBody))
	if err != nil {
		return returnErr(fmt.Errorf("UAST Reflector Server mati atau terputus: %v", err)), true
	}
	defer resp.Body.Close()

	var resultPayload map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&resultPayload); err != nil {
		return returnErr(fmt.Errorf("Gagal membaca hasil Reflector: %v", err)), true
	}

	if resp.StatusCode == 200 {
		return returnOk(resultPayload), true
	}

	errDetail, _ := resultPayload["error"].(string)
	return returnErr(fmt.Errorf("Reflector Error: %s", errDetail)), true
}
