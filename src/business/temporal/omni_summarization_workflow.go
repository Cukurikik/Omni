package omnitemporal

import (
	"context"
	"time"

	"go.temporal.io/sdk/workflow"
)

// OMNI Framework - Temporal SDK Workflow for Liputan6 Summarization
// Handles long-running abstractive summarization jobs asynchronously

type SummarizationResult struct {
	DocumentID string
	Summary    string
}

func OmniSummarizationWorkflow(ctx workflow.Context, documentID string, text string) (SummarizationResult, error) {
	options := workflow.ActivityOptions{
		StartToCloseTimeout: time.Minute * 5,
	}
	ctx = workflow.WithActivityOptions(ctx, options)

	var result SummarizationResult

	// Execute the activity which talks to the Python HuggingFace backend
	err := workflow.ExecuteActivity(ctx, OmniSummarizationActivity, documentID, text).Get(ctx, &result)
	if err != nil {
		return SummarizationResult{}, err
	}

	return result, nil
}

// OmniSummarizationActivity mocks the actual activity implementation for the workflow
func OmniSummarizationActivity(ctx context.Context, docID string, text string) (SummarizationResult, error) {
	// Call Python Backend via gRPC
	return SummarizationResult{
		DocumentID: docID,
		Summary:    "OMNI Framework produced abstractive summary...",
	}, nil
}
