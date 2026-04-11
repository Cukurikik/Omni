package cloud_apis

import (
	"context"
	"fmt"
	"log"

	"cloud.google.com/go/firestore"
	firebase "firebase.google.com/go/v4"
	"google.golang.org/api/iterator"
	"google.golang.org/api/option"
)

// ==========================================
// 🗄️ OMNI FIREBASE FIRESTORE — NOSQL DATABASE
// ==========================================
// Firestore memberikan real-time NoSQL document database yang scalable.
//
// OMNI Framework menggunakan Firestore untuk:
//   - Tenant configuration storage
//   - Real-time state synchronization (dashboard, chat)
//   - Offline-first mobile data via OMNI Swift layer
//   - Serverless backend data layer
//
// Target ARR: +$30.000 via SaaS tenant data storage
// ==========================================

// FirestoreBridge menyediakan akses native ke Cloud Firestore
type FirestoreBridge struct {
	projectID      string
	credentialPath string
}

// NewFirestoreBridge membuat bridge baru ke Firestore
func NewFirestoreBridge(projectID, credentialPath string) *FirestoreBridge {
	return &FirestoreBridge{
		projectID:      projectID,
		credentialPath: credentialPath,
	}
}

// getClient menginisialisasi Firestore client melalui Firebase App
func (f *FirestoreBridge) getClient(ctx context.Context) (*firestore.Client, error) {
	var app *firebase.App
	var err error

	if f.credentialPath != "" {
		opt := option.WithCredentialsFile(f.credentialPath)
		app, err = firebase.NewApp(ctx, nil, opt)
	} else {
		app, err = firebase.NewApp(ctx, nil)
	}
	if err != nil {
		return nil, fmt.Errorf("OMNI_FIRESTORE_ERROR: gagal inisialisasi app: %v", err)
	}

	client, err := app.Firestore(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_FIRESTORE_ERROR: gagal membuat client: %v", err)
	}
	return client, nil
}

// SetDocument membuat atau menimpa dokumen di collection yang ditentukan
func (f *FirestoreBridge) SetDocument(ctx context.Context, collection, docID string, data map[string]interface{}) error {
	client, err := f.getClient(ctx)
	if err != nil {
		return err
	}
	defer client.Close()

	_, err = client.Collection(collection).Doc(docID).Set(ctx, data)
	if err != nil {
		return fmt.Errorf("OMNI_FIRESTORE_ERROR: gagal menulis dokumen %s/%s: %v", collection, docID, err)
	}

	log.Printf("🗄️ [OMNI FIRESTORE] Dokumen ditulis: %s/%s", collection, docID)
	return nil
}

// GetDocument membaca dokumen tunggal berdasarkan collection dan document ID
func (f *FirestoreBridge) GetDocument(ctx context.Context, collection, docID string) (map[string]interface{}, error) {
	client, err := f.getClient(ctx)
	if err != nil {
		return nil, err
	}
	defer client.Close()

	doc, err := client.Collection(collection).Doc(docID).Get(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_FIRESTORE_ERROR: gagal membaca dokumen %s/%s: %v", collection, docID, err)
	}

	log.Printf("🗄️ [OMNI FIRESTORE] Dokumen dibaca: %s/%s", collection, docID)
	return doc.Data(), nil
}

// QueryCollection menjalankan query terhadap collection dengan filter
func (f *FirestoreBridge) QueryCollection(ctx context.Context, collection, field, op string, value interface{}) ([]map[string]interface{}, error) {
	client, err := f.getClient(ctx)
	if err != nil {
		return nil, err
	}
	defer client.Close()

	iter := client.Collection(collection).Where(field, op, value).Documents(ctx)
	defer iter.Stop()

	var results []map[string]interface{}
	for {
		doc, err := iter.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return results, fmt.Errorf("OMNI_FIRESTORE_ERROR: gagal iterasi query: %v", err)
		}
		results = append(results, doc.Data())
	}

	log.Printf("🗄️ [OMNI FIRESTORE] Query selesai: %d dokumen ditemukan", len(results))
	return results, nil
}

// DeleteDocument menghapus dokumen dari collection
func (f *FirestoreBridge) DeleteDocument(ctx context.Context, collection, docID string) error {
	client, err := f.getClient(ctx)
	if err != nil {
		return err
	}
	defer client.Close()

	_, err = client.Collection(collection).Doc(docID).Delete(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_FIRESTORE_ERROR: gagal menghapus dokumen %s/%s: %v", collection, docID, err)
	}

	log.Printf("🗄️ [OMNI FIRESTORE] Dokumen dihapus: %s/%s", collection, docID)
	return nil
}

// BatchWrite menulis banyak dokumen sekaligus dalam satu operasi atomik
func (f *FirestoreBridge) BatchWrite(ctx context.Context, collection string, docs map[string]map[string]interface{}) error {
	client, err := f.getClient(ctx)
	if err != nil {
		return err
	}
	defer client.Close()

	batch := client.Batch()
	for docID, data := range docs {
		ref := client.Collection(collection).Doc(docID)
		batch.Set(ref, data)
	}

	_, err = batch.Commit(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_FIRESTORE_ERROR: gagal batch write ke %s: %v", collection, err)
	}

	log.Printf("🗄️ [OMNI FIRESTORE] Batch write selesai: %d dokumen ke '%s'", len(docs), collection)
	return nil
}
