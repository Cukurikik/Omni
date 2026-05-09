package network_gocore

import (
	"encoding/json"
	"fmt"
	"net/http"
)

// GithubPRWebhookHandler triggers the Autonomous Code Reviewer on PR events.
type GithubPRWebhookHandler struct {
	SecretToken string
}

func NewGithubPRWebhookHandler(token string) *GithubPRWebhookHandler {
	return &GithubPRWebhookHandler{SecretToken: token}
}

type PRWebhookPayload struct {
	Action      string `json:"action"`
	PullRequest struct {
		Number  int    `json:"number"`
		State   string `json:"state"`
		DiffURL string `json:"diff_url"`
	} `json:"pull_request"`
}

func (h *GithubPRWebhookHandler) HandleWebhook(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var payload PRWebhookPayload
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	if payload.Action == "opened" || payload.Action == "synchronize" {
		// OMNI Router: Trigger diff analyzer and LLM Review Engine
		fmt.Printf("Received PR event for PR #%d. Triggering OMNI Code Reviewer.\n", payload.PullRequest.Number)
	}

	w.WriteHeader(http.StatusOK)
}

