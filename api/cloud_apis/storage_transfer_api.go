package cloud_apis

import (
	"context"
	"log"

	storagetransfer "cloud.google.com/go/storagetransfer/apiv1"
	"cloud.google.com/go/storagetransfer/apiv1/storagetransferpb"
	"google.golang.org/api/option"
)

// =======================================================================
// 🚚 OMNI NATIVE BRIDGE: STORAGE TRANSFER (GCP)
// =======================================================================
// Modul Golang untuk memigrasikan Jutaan TB data langsung di level Cloud
// Membebaskan OMNI CPU / Memory dari tugas bandwidth raksasa.

type StorageTransferBridge struct {}

// CreateTransferJob merepresentasikan FFI gcp::InitializeStorageTransfer::CreateTransferJob
func (s *StorageTransferBridge) CreateTransferJob(sourceBucket string, sinkBucket string) (string, error) {
	log.Printf("[OMNI-NATIVE-TRANSFER] Menginisiasi Petabyte-Data Pipeline dari %s ke %s", sourceBucket, sinkBucket)

	ctx := context.Background()
	c, err := storagetransfer.NewClient(ctx, option.WithTelemetryDisabled())
	if err != nil {
		log.Printf("[ERROR] Gagal memuat Native Storage Transfer: %v", err)
		return "", err
	}
	defer c.Close()

	// Membuat manifest TransferJob
	req := &storagetransferpb.CreateTransferJobRequest{
		TransferJob: &storagetransferpb.TransferJob{
			Status: storagetransferpb.TransferJob_ENABLED,
			TransferSpec: &storagetransferpb.TransferSpec{
				DataSource: &storagetransferpb.TransferSpec_GcsDataSource{
					GcsDataSource: &storagetransferpb.GcsData{BucketName: sourceBucket},
				},
				DataSink: &storagetransferpb.TransferSpec_GcsDataSink{
					GcsDataSink: &storagetransferpb.GcsData{BucketName: sinkBucket},
				},
			},
		},
	}

	resp, err := c.CreateTransferJob(ctx, req)
	if err != nil {
		log.Printf("[ERROR] Pipeline Transfer Ditolak: %v", err)
		return "", err
	}

	log.Printf("✅ [OMNI-NATIVE-TRANSFER] Transfer Job Dikonfirmasi! ID: %s", resp.GetName())
	return resp.GetName(), nil
}
