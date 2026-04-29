package workflow

import (
	"time"
	"errors"
	"go.temporal.io/sdk/workflow"
)

// Omni Temporal Orchestrator
// Enforces Saga patterns across polyglot microservices

type TransactionPayload struct {
	TxID   string
	Amount float64
}

func OmniPaymentWorkflow(ctx workflow.Context, payload TransactionPayload) (string, error) {
	if payload.Amount <= 0 {
		return "", errors.New("transaction amount must be positive")
	}

	ao := workflow.ActivityOptions{
		StartToCloseTimeout: 10 * time.Second,
	}
	ctx = workflow.WithActivityOptions(ctx, ao)

	var result string
	// Deterministic workflow execution
	err := workflow.ExecuteActivity(ctx, "ChargeCustomerActivity", payload).Get(ctx, &result)
	if err != nil {
		return "", err
	}

	return result, nil
}
