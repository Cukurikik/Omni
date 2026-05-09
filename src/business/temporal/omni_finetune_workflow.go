// OMNI Business — Temporal Distributed Workflow
// Orchestrates distributed LLM fine-tuning pipelines across clusters

package omnitemporal

import (
	"time"

	"go.temporal.io/sdk/workflow"
)

// FineTuneWorkflow definition
func FineTuneWorkflow(ctx workflow.Context, datasetID string, modelParams map[string]interface{}) (string, error) {
	ao := workflow.ActivityOptions{
		StartToCloseTimeout: 12 * time.Hour,
	}
	ctx = workflow.WithActivityOptions(ctx, ao)

	logger := workflow.GetLogger(ctx)
	logger.Info("OMNI Fine-tune workflow started", "DatasetID", datasetID)

	var dataRef string
	err := workflow.ExecuteActivity(ctx, "PrepareDatasetActivity", datasetID).Get(ctx, &dataRef)
	if err != nil {
		return "", err
	}

	var checkpoint string
	err = workflow.ExecuteActivity(ctx, "ExecuteTrainingActivity", dataRef, modelParams).Get(ctx, &checkpoint)
	if err != nil {
		return "", err
	}

	var finalModelRef string
	err = workflow.ExecuteActivity(ctx, "ExportAndRegisterModelActivity", checkpoint).Get(ctx, &finalModelRef)
	if err != nil {
		return "", err
	}

	logger.Info("OMNI Fine-tune workflow completed successfully", "ModelRef", finalModelRef)
	return finalModelRef, nil
}
