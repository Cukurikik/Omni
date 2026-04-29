package llm_api

import (
	"net/http"
	"github.com/omni/core/result"
)

func HandleLLMRequest(w http.ResponseWriter, r *http.Request) result.Result[bool] {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return result.Err[bool](nil)
	}
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{"status":"success"}`))
	return result.Ok(true)
}
