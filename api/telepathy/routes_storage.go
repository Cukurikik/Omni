package telepathy

import (
	"context"

	"omnitools/cloud_apis"
)

// RoutesStorage menangani GCS Storage dan Storage Transfer
func RoutesStorage(ctx context.Context, method string, args map[string]interface{}, ok func(interface{}) OmniResponse, fail func(error) OmniResponse) (OmniResponse, bool) {
	projectId, _ := args["projectId"].(string)

	switch method {

	// ── GCS STORAGE ─────────────────────────────────────────────────
	case "gcp::Storage::ListBuckets":
		if cloud_apis.GCS == nil {
			_ = cloud_apis.InitializeGCSClient()
		}
		if cloud_apis.GCS != nil {
			res, err := cloud_apis.GCS.ListBuckets(projectId)
			if err != nil { return fail(err), true }
			return ok(res), true
		}
		return ok("GCS not initialized"), true

	case "gcp::Storage::CreateBucket":
		bucketName, _ := args["bucketName"].(string)
		location, _ := args["location"].(string)
		if cloud_apis.GCS == nil {
			_ = cloud_apis.InitializeGCSClient()
		}
		if cloud_apis.GCS != nil {
			err := cloud_apis.GCS.CreateBucket(projectId, bucketName, location)
			if err != nil { return fail(err), true }
			return ok("Bucket created"), true
		}
		return ok("GCS not initialized"), true

	case "gcp::Storage::DeleteBucket":
		bucketName, _ := args["bucketName"].(string)
		if cloud_apis.GCS == nil {
			_ = cloud_apis.InitializeGCSClient()
		}
		if cloud_apis.GCS != nil {
			err := cloud_apis.GCS.DeleteBucket(bucketName)
			if err != nil { return fail(err), true }
			return ok("Bucket deleted"), true
		}
		return ok("GCS not initialized"), true

	case "gcp::Storage::DeleteObject":
		bucketName, _ := args["bucketName"].(string)
		objectName, _ := args["objectName"].(string)
		if cloud_apis.GCS == nil {
			_ = cloud_apis.InitializeGCSClient()
		}
		if cloud_apis.GCS != nil {
			err := cloud_apis.GCS.DeleteObject(bucketName, objectName)
			if err != nil { return fail(err), true }
			return ok("Object deleted"), true
		}
		return ok("GCS not initialized"), true
	}

	return OmniResponse{}, false
}
