package temporal

import (
	"time"
	"go.temporal.io/sdk/workflow"
)

func ARISResearchWorkflow(ctx workflow.Context, topic string) (string, error) {
	ao := workflow.ActivityOptions{
		StartToCloseTimeout: 2 * time.Hour,
	}
	ctx = workflow.WithActivityOptions(ctx, ao)

	var draft string
	// Run Sleep Research Activity
	err := workflow.ExecuteActivity(ctx, "SleepResearchActivity", topic).Get(ctx, &draft)
	if err != nil {
		return "", err
	}

	return draft, nil
}
