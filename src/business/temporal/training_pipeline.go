package omnitemporal

import (
	"time"

	"go.temporal.io/sdk/workflow"
)

type TrainingParams struct {
	DatasetID string
	ModelType string
}

type TrainingResult struct {
	ModelURL string
	Accuracy float64
}

func ModelTrainingWorkflow(ctx workflow.Context, params TrainingParams) (*TrainingResult, error) {
	ao := workflow.ActivityOptions{
		StartToCloseTimeout: time.Hour,
	}
	ctx = workflow.WithActivityOptions(ctx, ao)

	var result TrainingResult
	// Call PrepareData Activity
	err := workflow.ExecuteActivity(ctx, "PrepareDataActivity", params.DatasetID).Get(ctx, nil)
	if err != nil {
		return nil, err
	}

	// Call TrainModel Activity
	err = workflow.ExecuteActivity(ctx, "TrainModelActivity", params.ModelType).Get(ctx, &result)
	if err != nil {
		return nil, err
	}

	return &result, nil
}
