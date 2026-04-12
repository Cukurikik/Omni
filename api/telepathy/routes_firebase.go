package telepathy

import (
	"context"

	"omnitools/cloud_apis"
)

// RoutesFirebase menangani semua Firebase services
func RoutesFirebase(ctx context.Context, method string, args map[string]interface{}, ok func(interface{}) OmniResponse, fail func(error) OmniResponse) (OmniResponse, bool) {
	projectId, _ := args["projectId"].(string)
	credPath, _ := args["credentialPath"].(string)

	switch method {

	// ── FIREBASE AUTH ────────────────────────────────────────────────
	case "gcp::FirebaseAuth::GetUser":
		uid, _ := args["uid"].(string)
		bridge := cloud_apis.NewFirebaseAuthBridge(projectId, credPath)
		res, err := bridge.GetUser(ctx, uid)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::FirebaseAuth::CreateUser":
		email, _ := args["email"].(string)
		password, _ := args["password"].(string)
		displayName, _ := args["displayName"].(string)
		bridge := cloud_apis.NewFirebaseAuthBridge(projectId, credPath)
		res, err := bridge.CreateUser(ctx, email, password, displayName)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::FirebaseAuth::DeleteUser":
		uid, _ := args["uid"].(string)
		bridge := cloud_apis.NewFirebaseAuthBridge(projectId, credPath)
		err := bridge.DeleteUser(ctx, uid)
		if err != nil { return fail(err), true }
		return ok("User deleted"), true

	case "gcp::FirebaseAuth::VerifyIDToken":
		idToken, _ := args["idToken"].(string)
		bridge := cloud_apis.NewFirebaseAuthBridge(projectId, credPath)
		res, err := bridge.VerifyIDToken(ctx, idToken)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── FIREBASE FIRESTORE ──────────────────────────────────────────
	case "gcp::Firestore::GetDocument":
		collection, _ := args["collection"].(string)
		docId, _ := args["documentId"].(string)
		bridge := cloud_apis.NewFirestoreBridge(projectId, credPath)
		res, err := bridge.GetDocument(ctx, collection, docId)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::Firestore::SetDocument":
		collection, _ := args["collection"].(string)
		docId, _ := args["documentId"].(string)
		data, _ := args["data"].(map[string]interface{})
		bridge := cloud_apis.NewFirestoreBridge(projectId, credPath)
		err := bridge.SetDocument(ctx, collection, docId, data)
		if err != nil { return fail(err), true }
		return ok("Document set"), true

	case "gcp::Firestore::DeleteDocument":
		collection, _ := args["collection"].(string)
		docId, _ := args["documentId"].(string)
		bridge := cloud_apis.NewFirestoreBridge(projectId, credPath)
		err := bridge.DeleteDocument(ctx, collection, docId)
		if err != nil { return fail(err), true }
		return ok("Document deleted"), true

	// ── FIREBASE FCM ────────────────────────────────────────────────
	case "gcp::FCM::SendToDevice":
		token, _ := args["token"].(string)
		title, _ := args["title"].(string)
		body, _ := args["body"].(string)
		bridge := cloud_apis.NewFCMBridge(projectId, credPath)
		res, err := bridge.SendToDevice(ctx, token, title, body, nil)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::FCM::SendToTopic":
		topic, _ := args["topic"].(string)
		title, _ := args["title"].(string)
		body, _ := args["body"].(string)
		bridge := cloud_apis.NewFCMBridge(projectId, credPath)
		res, err := bridge.SendToTopic(ctx, topic, title, body, nil)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── FIREBASE HOSTING ────────────────────────────────────────────
	case "gcp::FirebaseHosting::ListChannels":
		siteId, _ := args["siteId"].(string)
		bridge := cloud_apis.NewFirebaseHostingBridge(projectId, siteId)
		res, err := bridge.ListChannels(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::FirebaseHosting::GetSiteURL":
		siteId, _ := args["siteId"].(string)
		bridge := cloud_apis.NewFirebaseHostingBridge(projectId, siteId)
		return ok(bridge.GetSiteURL()), true

	// ── FIREBASE STORAGE ────────────────────────────────────────────
	case "gcp::FirebaseStorage::DeleteFile":
		objectPath, _ := args["objectPath"].(string)
		bucketName, _ := args["bucketName"].(string)
		bridge := cloud_apis.NewFirebaseStorageBridge(projectId, bucketName, credPath)
		err := bridge.DeleteFile(ctx, objectPath)
		if err != nil { return fail(err), true }
		return ok("File deleted"), true

	// ── FIREBASE APP CHECK ──────────────────────────────────────────
	case "gcp::AppCheck::VerifyToken":
		token, _ := args["token"].(string)
		bridge := cloud_apis.NewAppCheckBridge(projectId, credPath)
		res, err := bridge.VerifyToken(ctx, token)
		if err != nil { return fail(err), true }
		return ok(res), true
	}

	return OmniResponse{}, false
}
