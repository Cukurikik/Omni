package telepathy

import (
	"context"
	"fmt"
	"log"

	"omnitools/cloud_apis"
	"omnitools/services"
)

// OmniRequest merepresentasikan standar input dari invokasi OmniNativeBridge layer (TypeScript / Swift)
type OmniRequest struct {
	Method string                 `json:"method"`
	Args   map[string]interface{} `json:"args"`
}

// OmniResponse merepresentasikan standar Monadic Response sesuai panduan Blueprint v2.0
type OmniResponse struct {
	Status string      `json:"status"` // "Ok" atau "Err"
	Data   interface{} `json:"data,omitempty"`
	Error  string      `json:"error,omitempty"`
}

// TelepathyRouter adalah inti dari sistem saraf OMNI Backend.
// Menerapkan "Lazy-Initialization" dan mendelegasikan ke sub-routers per domain.
func TelepathyRouter(ctx context.Context, req OmniRequest) OmniResponse {
	log.Printf("[OMNI-TELEPATHY] Incoming invoke: %s", req.Method)

	// Helper Monadic Error
	returnErr := func(err error) OmniResponse {
		log.Printf("[OMNI-TELEPATHY ERR] %s -> %v", req.Method, err)
		return OmniResponse{Status: "Err", Error: err.Error()}
	}

	// Helper Monadic Success
	returnOk := func(data interface{}) OmniResponse {
		return OmniResponse{Status: "Ok", Data: data}
	}

	// =========================================================================
	// WAVE 15: NEURAL WIRING — DOMAIN SUB-ROUTER DISPATCH
	// =========================================================================
	// Setiap domain sub-router mengembalikan (OmniResponse, handled bool).
	// Jika handled == true, router berhenti di sini.

	if res, handled := RoutesCompute(ctx, req.Method, req.Args, returnOk, returnErr); handled {
		return res
	}
	if res, handled := RoutesData(ctx, req.Method, req.Args, returnOk, returnErr); handled {
		return res
	}
	if res, handled := RoutesAI(ctx, req.Method, req.Args, returnOk, returnErr); handled {
		return res
	}
	if res, handled := RoutesOps(ctx, req.Method, req.Args, returnOk, returnErr); handled {
		return res
	}
	if res, handled := RoutesNetwork(ctx, req.Method, req.Args, returnOk, returnErr); handled {
		return res
	}
	if res, handled := RoutesStorage(ctx, req.Method, req.Args, returnOk, returnErr); handled {
		return res
	}
	if res, handled := RoutesSecurity(ctx, req.Method, req.Args, returnOk, returnErr); handled {
		return res
	}
	if res, handled := RoutesFirebase(ctx, req.Method, req.Args, returnOk, returnErr); handled {
		return res
	}
	if res, handled := RoutesOrchestrators(ctx, req.Method, req.Args, returnOk, returnErr); handled {
		return res
	}
	if res, handled := RoutesModels(ctx, req.Method, req.Args, returnOk, returnErr); handled {
		return res
	}
	if res, handled := RoutesLegacy(ctx, req.Method, req.Args, returnOk, returnErr); handled {
		return res
	}
	if res, handled := RoutesReflector(ctx, req.Method, req.Args, returnOk, returnErr); handled {
		return res
	}
	if res, handled := RoutesObservability(ctx, req.Method, req.Args, returnOk, returnErr); handled {
		return res
	}
	if res, handled := RoutesSingularity(ctx, req.Method, req.Args, returnOk, returnErr); handled {
		return res
	}

	// =========================================================================
	// LEGACY ROUTES (Wave 6-9) — Tetap dipertahankan untuk backward compat
	// =========================================================================
	switch req.Method {

	// ── SERVICE USAGE & QUOTAS ───────────────────────────────────────
	case "gcp::ServiceUsageBridge::ListEnabledServices":
		projectName, _ := req.Args["projectName"].(string)
		client, err := cloud_apis.NewServiceUsageManager(ctx)
		if err != nil { return returnErr(err) }
		defer client.Close()
		res, err := client.ListEnabledServices(projectName)
		if err != nil { return returnErr(err) }
		return returnOk(res)

	case "gcp::ServiceUsageBridge::EnableService":
		projectName, _ := req.Args["projectName"].(string)
		serviceName, _ := req.Args["serviceName"].(string)
		client, err := cloud_apis.NewServiceUsageManager(ctx)
		if err != nil { return returnErr(err) }
		defer client.Close()
		err = client.EnableService(projectName, serviceName)
		if err != nil { return returnErr(err) }
		return returnOk("Service Enabled")

	case "gcp::ServiceUsageBridge::DisableService":
		projectName, _ := req.Args["projectName"].(string)
		serviceName, _ := req.Args["serviceName"].(string)
		client, err := cloud_apis.NewServiceUsageManager(ctx)
		if err != nil { return returnErr(err) }
		defer client.Close()
		err = client.DisableService(projectName, serviceName)
		if err != nil { return returnErr(err) }
		return returnOk("Service Disabled")

	case "gcp::CloudQuotasBridge::GetQuotaInfo":
		projectName, _ := req.Args["projectName"].(string)
		serviceName, _ := req.Args["serviceName"].(string)
		quotaId, _ := req.Args["quotaId"].(string)
		client, err := cloud_apis.NewCloudQuotasManager(ctx)
		if err != nil { return returnErr(err) }
		defer client.Close()
		res, err := client.GetQuotaInfo(projectName, serviceName, quotaId)
		if err != nil { return returnErr(err) }
		return returnOk(res)

	// ── BILLING ─────────────────────────────────────────────────────
	case "gcp::CloudBillingBridge::DisableBilling":
		projectId, _ := req.Args["projectId"].(string)
		client, err := cloud_apis.NewCloudBillingManager(ctx)
		if err != nil { return returnErr(err) }
		defer client.Close()
		res, err := client.DisableBilling(projectId)
		if err != nil { return returnErr(err) }
		return returnOk(res)

	// ── PAAS ORCHESTRATOR ───────────────────────────────────────────
	case "gcp::CloudPaaSBridge::DeployApp":
		tenantId, _ := req.Args["tenantId"].(string)
		projectId, _ := req.Args["projectId"].(string)
		appName, _ := req.Args["appName"].(string)
		dockerImage, _ := req.Args["dockerImage"].(string)
		res, err := services.DeployOMNICloudApp(ctx, tenantId, projectId, appName, dockerImage)
		if err != nil { return returnErr(err) }
		return returnOk(res)

	// ── FALLBACK ────────────────────────────────────────────────────
	default:
		return OmniResponse{
			Status: "Err",
			Error:  fmt.Sprintf("OMNI Error E001: Method %s belum terdaftar di Telepathy Router", req.Method),
		}
	}
}
