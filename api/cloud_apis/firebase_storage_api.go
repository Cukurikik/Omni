package cloud_apis

import (
	"context"
	"fmt"
	"io"
	"log"
	"time"

	"cloud.google.com/go/storage"
	firebase "firebase.google.com/go/v4"
	"google.golang.org/api/option"
)

// ==========================================
// 📁 OMNI FIREBASE STORAGE — FILE & MEDIA UPLOAD
// ==========================================
// Firebase Storage (backed by Cloud Storage) menyediakan penyimpanan
// file terstruktur dan aman untuk aplikasi.
//
// OMNI Framework menggunakan Firebase Storage untuk:
//   - Upload gambar profil, dokumen KYC
//   - Media storage untuk Imagen/Veo generated content
//   - Backup data terenkripsi (KMS envelope encryption)
//
// Target ARR: +$20.000 via media storage tier
// ==========================================

// FirebaseStorageBridge menyediakan akses ke Firebase Storage (Cloud Storage bucket)
type FirebaseStorageBridge struct {
	projectID      string
	bucketName     string
	credentialPath string
}

// NewFirebaseStorageBridge membuat bridge baru ke Firebase Storage
func NewFirebaseStorageBridge(projectID, bucketName, credentialPath string) *FirebaseStorageBridge {
	if bucketName == "" {
		bucketName = projectID + ".appspot.com"
	}
	return &FirebaseStorageBridge{
		projectID:      projectID,
		bucketName:     bucketName,
		credentialPath: credentialPath,
	}
}

// getBucket menginisialisasi Firebase App dan mengembalikan storage bucket handle
func (f *FirebaseStorageBridge) getBucket(ctx context.Context) (*storage.BucketHandle, error) {
	var app *firebase.App
	var err error

	conf := &firebase.Config{
		StorageBucket: f.bucketName,
	}

	if f.credentialPath != "" {
		opt := option.WithCredentialsFile(f.credentialPath)
		app, err = firebase.NewApp(ctx, conf, opt)
	} else {
		app, err = firebase.NewApp(ctx, conf)
	}
	if err != nil {
		return nil, fmt.Errorf("OMNI_FIREBASE_STORAGE_ERROR: gagal inisialisasi app: %v", err)
	}

	client, err := app.Storage(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_FIREBASE_STORAGE_ERROR: gagal membuat storage client: %v", err)
	}

	bucket, err := client.DefaultBucket()
	if err != nil {
		return nil, fmt.Errorf("OMNI_FIREBASE_STORAGE_ERROR: gagal mengakses bucket default: %v", err)
	}

	return bucket, nil
}

// UploadFile mengunggah file ke Firebase Storage
func (f *FirebaseStorageBridge) UploadFile(ctx context.Context, objectPath string, reader io.Reader, contentType string) error {
	bucket, err := f.getBucket(ctx)
	if err != nil {
		return err
	}

	writer := bucket.Object(objectPath).NewWriter(ctx)
	writer.ContentType = contentType
	writer.Metadata = map[string]string{
		"uploaded-by": "omni-framework",
		"timestamp":   time.Now().UTC().Format(time.RFC3339),
	}

	if _, err := io.Copy(writer, reader); err != nil {
		return fmt.Errorf("OMNI_FIREBASE_STORAGE_ERROR: gagal menulis file '%s': %v", objectPath, err)
	}

	if err := writer.Close(); err != nil {
		return fmt.Errorf("OMNI_FIREBASE_STORAGE_ERROR: gagal menutup writer untuk '%s': %v", objectPath, err)
	}

	log.Printf("📁 [OMNI STORAGE] File berhasil diunggah: gs://%s/%s", f.bucketName, objectPath)
	return nil
}

// DownloadFile mengunduh file dari Firebase Storage
func (f *FirebaseStorageBridge) DownloadFile(ctx context.Context, objectPath string, writer io.Writer) error {
	bucket, err := f.getBucket(ctx)
	if err != nil {
		return err
	}

	reader, err := bucket.Object(objectPath).NewReader(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_FIREBASE_STORAGE_ERROR: gagal membaca '%s': %v", objectPath, err)
	}
	defer reader.Close()

	if _, err := io.Copy(writer, reader); err != nil {
		return fmt.Errorf("OMNI_FIREBASE_STORAGE_ERROR: gagal mengunduh '%s': %v", objectPath, err)
	}

	log.Printf("📁 [OMNI STORAGE] File berhasil diunduh: gs://%s/%s", f.bucketName, objectPath)
	return nil
}

// DeleteFile menghapus file dari Firebase Storage
func (f *FirebaseStorageBridge) DeleteFile(ctx context.Context, objectPath string) error {
	bucket, err := f.getBucket(ctx)
	if err != nil {
		return err
	}

	err = bucket.Object(objectPath).Delete(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_FIREBASE_STORAGE_ERROR: gagal menghapus '%s': %v", objectPath, err)
	}

	log.Printf("📁 [OMNI STORAGE] File berhasil dihapus: gs://%s/%s", f.bucketName, objectPath)
	return nil
}

// GenerateSignedURL membuat URL download sementara yang aman (default: 15 menit)
func (f *FirebaseStorageBridge) GenerateSignedURL(ctx context.Context, objectPath string, expiration time.Duration) (string, error) {
	bucket, err := f.getBucket(ctx)
	if err != nil {
		return "", err
	}

	opts := &storage.SignedURLOptions{
		Method:  "GET",
		Expires: time.Now().Add(expiration),
	}

	url, err := bucket.SignedURL(objectPath, opts)
	if err != nil {
		return "", fmt.Errorf("OMNI_FIREBASE_STORAGE_ERROR: gagal generate signed URL: %v", err)
	}

	log.Printf("📁 [OMNI STORAGE] Signed URL dibuat: %s (expires: %v)", objectPath, expiration)
	return url, nil
}
