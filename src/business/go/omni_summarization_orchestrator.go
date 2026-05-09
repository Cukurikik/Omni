package business

import (
	"bytes"
	"encoding/json"
	"net/http"
	"time"
)

type SummaryRequest struct {
	Text string `json:"text"`
}

type SummaryResponse struct {
	Summary string `json:"summary"`
}

// OmniSummarizationService coordinates with Python Abstractive Model
func OmniSummarizationService(textContent string) (string, error) {
	reqBody, _ := json.Marshal(SummaryRequest{Text: textContent})

	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Post("http://omni-compute-python:8080/summarize", "application/json", bytes.NewBuffer(reqBody))

	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var res SummaryResponse
	json.NewDecoder(resp.Body).Decode(&res)
	return res.Summary, nil
}
