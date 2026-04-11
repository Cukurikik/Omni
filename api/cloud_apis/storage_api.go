package cloud_apis

import (
	"context"
	"fmt"
	"io"
	"log"
	"time"

	"cloud.google.com/go/storage"
)

// ==========================================
// ☁️ OMNI CLOUD APIs: GCS (Google Cloud Storage)
// ==========================================

type OmniStorageClient struct {
	client *storage.Client
	ctx    context.Context
}

var GCS *OmniStorageClient

// InitializeGCSClient mengaktifkan klien gRPC asli (Autentik) ke jaringan Google Storage.
func InitializeGCSClient() error {
	ctx := context.Background()
	
	// GOOGLE_APPLICATION_CREDENTIALS dibaca otomatis dari OMNI OS Environment
	client, err := storage.NewClient(ctx)
	if err != nil {
		return fmt.Errorf("omni-gcp: gagal membuat klien Storage. Konfigurasi kredensial Service Account buram: %v", err)
	}

	GCS = &OmniStorageClient{
		client: client,
		ctx:    ctx,
	}

	log.Println("✅ [CLOUD APIs] Modul Asli Google Cloud Storage telah Terhubung!")
	return nil
}

// UploadDirectStream memotong perantara (buffer disk lokal) 
// dan mengangkat data mentah sejuta gigabytes langsung ke GCS Bucket sebagai blob.
// (Menggantikan simulasi io.Discard di quarantine.go sebelumnya)
func (s *OmniStorageClient) UploadDirectStream(bucketName, objectName string, dataStream io.Reader) (int64, error) {
	if s.client == nil {
		return 0, fmt.Errorf("OMNI-GCS uninitialized")
	}

	start := time.Now()
	bucket := s.client.Bucket(bucketName)
	obj := bucket.Object(objectName)

	// Pembuatan Writer Object GCS murni (Pipe Streaming yang asli)
	writer := obj.NewWriter(s.ctx)
	// Kita bisa mengunci ChunkSize untuk mengakselerasi proses paralel
	writer.ChunkSize = 100 * 1024 * 1024 // 100 MB per chunk kompresi memory

	written, err := io.Copy(writer, dataStream)
	
	if errClose := writer.Close(); errClose != nil {
		return 0, fmt.Errorf("gagal menutup GCS StreamWriter: %v", errClose)
	}

	if err != nil {
		return 0, fmt.Errorf("gagal melempar byte gRPC ke Google Storage: %v", err)
	}

	log.Printf("☁️ [API GCS] Murni %d MB tersedot ke Bucket %s dalam %.2fs", 
		written/(1024*1024), bucketName, time.Since(start).Seconds())
	
	return written, nil
}
