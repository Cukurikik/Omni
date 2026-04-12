package telepathy

import (
	"context"

	"omnitools/cloud_apis"
)

// RoutesSecurity menangani KMS, Secret Manager, Security Center, DLP
func RoutesSecurity(ctx context.Context, method string, args map[string]interface{}, ok func(interface{}) OmniResponse, fail func(error) OmniResponse) (OmniResponse, bool) {
	projectId, _ := args["projectId"].(string)

	switch method {

	// ── KMS ──────────────────────────────────────────────────────────
	case "gcp::KMS::Encrypt":
		location, _ := args["location"].(string)
		keyRing, _ := args["keyRing"].(string)
		cryptoKey, _ := args["cryptoKey"].(string)
		plaintext, _ := args["plaintext"].(string)
		bridge := cloud_apis.NewKMSBridge(projectId, location, keyRing, cryptoKey)
		res, err := bridge.Encrypt(ctx, []byte(plaintext))
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::KMS::Decrypt":
		location, _ := args["location"].(string)
		keyRing, _ := args["keyRing"].(string)
		cryptoKey, _ := args["cryptoKey"].(string)
		ciphertext, _ := args["ciphertext"].(string)
		bridge := cloud_apis.NewKMSBridge(projectId, location, keyRing, cryptoKey)
		res, err := bridge.Decrypt(ctx, []byte(ciphertext))
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── SECRET MANAGER ──────────────────────────────────────────────
	case "gcp::SecretManager::GetSecret":
		secretName, _ := args["secretName"].(string)
		vault, err := cloud_apis.NewSecretVault(ctx, projectId)
		if err != nil { return fail(err), true }
		defer vault.Close()
		res, err := vault.GetSecret(ctx, secretName)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::SecretManager::CreateSecret":
		secretName, _ := args["secretName"].(string)
		value, _ := args["value"].(string)
		vault, err := cloud_apis.NewSecretVault(ctx, projectId)
		if err != nil { return fail(err), true }
		defer vault.Close()
		err = vault.CreateSecret(ctx, secretName, value)
		if err != nil { return fail(err), true }
		return ok("Secret created"), true

	case "gcp::SecretManager::ListSecrets":
		vault, err := cloud_apis.NewSecretVault(ctx, projectId)
		if err != nil { return fail(err), true }
		defer vault.Close()
		res, err := vault.ListSecrets(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── SECURITY CENTER ─────────────────────────────────────────────
	case "gcp::SecurityCenter::ListFindings":
		filter, _ := args["filter"].(string)
		bridge := cloud_apis.NewSecurityCenterBridge(projectId)
		res, err := bridge.ListFindings(ctx, filter)
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::SecurityCenter::ListSources":
		bridge := cloud_apis.NewSecurityCenterBridge(projectId)
		res, err := bridge.ListSources(ctx)
		if err != nil { return fail(err), true }
		return ok(res), true

	// ── DLP ─────────────────────────────────────────────────────────
	case "gcp::DLP::InspectText":
		text, _ := args["text"].(string)
		bridge := cloud_apis.NewDLPBridge(projectId)
		res, err := bridge.InspectText(ctx, text, []string{"PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD_NUMBER"})
		if err != nil { return fail(err), true }
		return ok(res), true

	case "gcp::DLP::DeidentifyText":
		text, _ := args["text"].(string)
		bridge := cloud_apis.NewDLPBridge(projectId)
		res, err := bridge.DeidentifyText(ctx, text, []string{"PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD_NUMBER"})
		if err != nil { return fail(err), true }
		return ok(res), true
	}

	return OmniResponse{}, false
}
