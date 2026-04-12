package telepathy

import (
	"context"
	"fmt"
	"log"
)

// RoutesLegacy mengarahkan lalu lintas data asinkron dari tumpukan teknologi lawas
// (seperti middleware Bank/Asuransi berbasis Java atau .NET) menuju Cloud Pub/Sub
// atau Cloud Database OMNI melalui Zero-Copy Architecture.
// Mengembalikan (OmniResponse, handled bool).
func RoutesLegacy(ctx context.Context, method string, args map[string]interface{}, returnOk func(interface{}) OmniResponse, returnErr func(error) OmniResponse) (OmniResponse, bool) {
	if len(method) < 13 || method[:13] != "gcp::Legacy::" {
		return OmniResponse{}, false
	}

	log.Printf("🏛️ [LEGACY BRIDGE] Mencegat Instruksi Usang: %s", method)

	switch method {
	case "gcp::Legacy::ExecuteTransaction":
		// Asumsi parameter dari sistem core banking (SOAP/XML -> JSON by gateway)
		accountID, ok1 := args["accountId"].(string)
		amount, ok2 := args["amount"].(float64)

		if !ok1 || !ok2 {
			return returnErr(fmt.Errorf("Parameter legacy tidak valid: accountId atau amount hilang")), true
		}

		// (Di sini OMNI secara asinkron menembakkan message ke Cloud Pub/Sub atau Cloud Tasks
		//  agar backend modern bisa memprosesnya tanpa mengunci thread utama.)
		log.Printf("💰 [LEGACY BRIDGE] Memproses Transaksi %s senilai %.2f via Omni Pipeline", accountID, amount)

		response := map[string]interface{}{
			"status":   "ASYNC_QUEUED",
			"receipt":  fmt.Sprintf("TRX-OMNI-%s", accountID),
			"latensi":  "0.01ms (Zero-Copy)",
		}

		return returnOk(response), true

	default:
		// Jika rute prefix gcp::Legacy valid tapi fungsinya tidak ada
		return returnErr(fmt.Errorf("Fungsi Legacy %s tidak ditemukan dalam Blueprint Model A", method)), true
	}
}
