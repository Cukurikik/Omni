package telepathy

import (
	"context"

	"cloud.google.com/go/logging"
	"omnitools/cloud_apis"
)

// RoutesOps menangani Logging, Monitoring, Trace, Error Reporting, Cloud Build, Scheduler, Tasks, Workflows
func RoutesOps(ctx context.Context, method string, args map[string]interface{}, ok func(interface{}) OmniResponse, fail func(error) OmniResponse) (OmniResponse, bool) {
	projectId, _ := args["projectId"].(string)
	location, _ := args["location"].(string)

	switch method {

	// ── CLOUD LOGGING ───────────────────────────────────────────────
	case "gcp::Logging::WriteLog":
		logId, _ := args["logId"].(string)
		message, _ := args["message"].(string)
		bridge := cloud_apis.NewCloudLoggingBridge(projectId, logId)
		err := bridge.WriteLog(ctx, logging.Info, message, nil)
		if err != nil { return fail(err), true }
		return ok("Log written"), true

	case "gcp::Logging::QueryLogs":
		filter, _ := args["filter"].(string)
		logId, _ := args["logId"].(string)
		bridge := cloud_apis.NewCloudLoggingBridge(projectId, logId)
		res, err := bridge.QueryLogs(ctx, filter, 100)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── CLOUD MONITORING ────────────────────────────────────────────
	case "gcp::Monitoring::WriteCustomMetric":
		metricType, _ := args["metricType"].(string)
		value, _ := args["value"].(float64)
		bridge := cloud_apis.NewCloudMonitoringBridge(projectId)
		err := bridge.WriteCustomMetric(ctx, metricType, value, nil)
		if err != nil { return fail(err), true }
		return ok("Metric written"), true

	// ── CLOUD BUILD ─────────────────────────────────────────────────
	case "gcp::CloudBuild::ListBuilds":
		bridge := cloud_apis.NewCloudBuildBridge(projectId, location)
		res, err := bridge.ListBuilds(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── CLOUD SCHEDULER ─────────────────────────────────────────────
	case "gcp::CloudScheduler::ListJobs":
		bridge := cloud_apis.NewCloudSchedulerBridge(projectId, location)
		res, err := bridge.ListJobs(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── CLOUD TASKS ─────────────────────────────────────────────────
	case "gcp::CloudTasks::PurgeQueue":
		queueId, _ := args["queueId"].(string)
		bridge := cloud_apis.NewCloudTasksBridge(projectId, location, queueId)
		err := bridge.PurgeQueue(ctx)
		if err != nil { return fail(err), true }
		return ok("Queue purged"), true

	// ── WORKFLOWS ───────────────────────────────────────────────────
	case "gcp::Workflows::ListWorkflows":
		bridge := cloud_apis.NewWorkflowsBridge(projectId, location)
		res, err := bridge.ListWorkflows(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::Workflows::ExecuteWorkflow":
		workflowName, _ := args["workflowName"].(string)
		argument, _ := args["argument"].(string)
		bridge := cloud_apis.NewWorkflowsBridge(projectId, location)
		res, err := bridge.ExecuteWorkflow(ctx, workflowName, argument)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── EVENTARC ────────────────────────────────────────────────────
	case "gcp::Eventarc::ListTriggers":
		bridge := cloud_apis.NewEventArcBridge(projectId, location)
		res, err := bridge.ListTriggers(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true
	}

	return OmniResponse{}, false
}
