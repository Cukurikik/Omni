package cloud_apis

import (
	"context"
	"fmt"
	"log"
	"time"

	"cloud.google.com/go/errorreporting"
)

// ==========================================
// 🚨 OMNI ERROR REPORTING — EXCEPTION TRACKING
// ==========================================

type ErrorReportingBridge struct {
	projectID   string
	serviceName string
}

func NewErrorReportingBridge(projectID, serviceName string) *ErrorReportingBridge {
	return &ErrorReportingBridge{projectID: projectID, serviceName: serviceName}
}

func (e *ErrorReportingBridge) ReportError(ctx context.Context, err error) error {
	client, clientErr := errorreporting.NewClient(ctx, e.projectID, errorreporting.Config{
		ServiceName: e.serviceName,
	})
	if clientErr != nil {
		return fmt.Errorf("OMNI_ERRREPORT_ERROR: gagal membuat client: %v", clientErr)
	}
	defer client.Close()
	defer client.Flush()

	client.Report(errorreporting.Entry{Error: err})
	log.Printf("🚨 [OMNI ERROR REPORTING] Error dilaporkan: %v", err)
	return nil
}

func (e *ErrorReportingBridge) ReportErrorWithContext(ctx context.Context, err error, user string, httpMethod string, url string) error {
	client, clientErr := errorreporting.NewClient(ctx, e.projectID, errorreporting.Config{
		ServiceName: e.serviceName,
	})
	if clientErr != nil {
		return fmt.Errorf("OMNI_ERRREPORT_ERROR: gagal membuat client: %v", clientErr)
	}
	defer client.Close()
	defer client.Flush()

	client.Report(errorreporting.Entry{
		Error: err,
		Req:   nil,
		User:  user,
	})
	log.Printf("🚨 [OMNI ERROR REPORTING] Error dilaporkan dari user '%s': %v", user, err)

	// Suppress unused warnings
	_ = httpMethod
	_ = url
	_ = time.Now()
	return nil
}
