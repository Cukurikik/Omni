package cloud_apis

import (
	"context"
	"fmt"
	"log"

	cloudtrace "cloud.google.com/go/trace/apiv2"
	"cloud.google.com/go/trace/apiv2/tracepb"
	"google.golang.org/protobuf/types/known/timestamppb"
	"google.golang.org/protobuf/types/known/wrapperspb"
	"time"
)

// ==========================================
// 🔍 OMNI CLOUD TRACE — DISTRIBUTED TRACING
// ==========================================

type CloudTraceBridge struct {
	projectID string
}

func NewCloudTraceBridge(projectID string) *CloudTraceBridge {
	return &CloudTraceBridge{projectID: projectID}
}

func (t *CloudTraceBridge) WriteSpan(ctx context.Context, traceID, spanID, displayName string, startTime, endTime time.Time) error {
	client, err := cloudtrace.NewClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_TRACE_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	spanName := fmt.Sprintf("projects/%s/traces/%s/spans/%s", t.projectID, traceID, spanID)

	_, err = client.CreateSpan(ctx, &tracepb.Span{
		Name:      spanName,
		SpanId:    spanID,
		DisplayName: &tracepb.TruncatableString{Value: displayName, TruncatedByteCount: 0},
		StartTime: timestamppb.New(startTime),
		EndTime:   timestamppb.New(endTime),
		SpanKind:  tracepb.Span_SERVER,
		ChildSpanCount: wrapperspb.Int32(0),
	})
	if err != nil {
		return fmt.Errorf("OMNI_TRACE_ERROR: gagal menulis span: %v", err)
	}
	log.Printf("🔍 [OMNI TRACE] Span ditulis: %s (%s)", displayName, spanID)
	return nil
}
