package cloud_apis

import (
	"context"
	"fmt"
	"log"

	workflows "cloud.google.com/go/workflows/apiv1"
	"cloud.google.com/go/workflows/apiv1/workflowspb"
	executions "cloud.google.com/go/workflows/executions/apiv1"
	"cloud.google.com/go/workflows/executions/apiv1/executionspb"
	"google.golang.org/api/iterator"
)

// ==========================================
// 🔄 OMNI WORKFLOWS — SERVERLESS ORCHESTRATION
// ==========================================

type WorkflowsBridge struct {
	projectID string
	location  string
}

func NewWorkflowsBridge(projectID, location string) *WorkflowsBridge {
	return &WorkflowsBridge{projectID: projectID, location: location}
}

func (w *WorkflowsBridge) parentPath() string {
	return fmt.Sprintf("projects/%s/locations/%s", w.projectID, w.location)
}

func (w *WorkflowsBridge) ListWorkflows(ctx context.Context) ([]*workflowspb.Workflow, error) {
	client, err := workflows.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_WORKFLOWS_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	it := client.ListWorkflows(ctx, &workflowspb.ListWorkflowsRequest{Parent: w.parentPath()})
	var wfs []*workflowspb.Workflow
	for {
		wf, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_WORKFLOWS_ERROR: gagal iterasi: %v", err)
		}
		wfs = append(wfs, wf)
	}
	log.Printf("🔄 [OMNI WORKFLOWS] Ditemukan %d workflows", len(wfs))
	return wfs, nil
}

func (w *WorkflowsBridge) ExecuteWorkflow(ctx context.Context, workflowName, argument string) (*executionspb.Execution, error) {
	client, err := executions.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_WORKFLOWS_ERROR: gagal membuat execution client: %v", err)
	}
	defer client.Close()

	exec, err := client.CreateExecution(ctx, &executionspb.CreateExecutionRequest{
		Parent: workflowName,
		Execution: &executionspb.Execution{
			Argument: argument,
		},
	})
	if err != nil {
		return nil, fmt.Errorf("OMNI_WORKFLOWS_ERROR: gagal execute workflow: %v", err)
	}
	log.Printf("🔄 [OMNI WORKFLOWS] Execution dimulai: %s", exec.Name)
	return exec, nil
}
