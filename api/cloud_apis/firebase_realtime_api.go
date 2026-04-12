package cloud_apis

import (
	"context"
	"fmt"

	firebase "firebase.google.com/go/v4"
	"firebase.google.com/go/v4/db"
)

// FirebaseRealtimeManager adalah wrapper OMNI-C/Rust Layer untuk GCP Realtime Database
type FirebaseRealtimeManager struct {
	client *db.Client
	ctx    context.Context
}

// NewFirebaseRealtimeManager menginisialisasi client Firebase RDB
func NewFirebaseRealtimeManager(ctx context.Context, app *firebase.App) (*FirebaseRealtimeManager, error) {
	client, err := app.Database(ctx)
	if err != nil {
		return nil, fmt.Errorf("omni.system.realtime: gagal inisialisasi - %w", err)
	}

	return &FirebaseRealtimeManager{
		client: client,
		ctx:    ctx,
	}, nil
}

// GetValue mengambil data langsung dari sebuah node dengan 0-copy OMNI bridge
func (m *FirebaseRealtimeManager) GetValue(path string) (map[string]interface{}, error) {
	ref := m.client.NewRef(path)
	var data map[string]interface{}
	if err := ref.Get(m.ctx, &data); err != nil {
		return nil, fmt.Errorf("omni.realtime.get: %w", err)
	}
	return data, nil
}

// SetValue menulis data secara langsung (Overwrite)
func (m *FirebaseRealtimeManager) SetValue(path string, data interface{}) error {
	ref := m.client.NewRef(path)
	if err := ref.Set(m.ctx, data); err != nil {
		return fmt.Errorf("omni.realtime.set: %w", err)
	}
	return nil
}

// UpdateValue melakukan partial update atau multi-path update atomik
func (m *FirebaseRealtimeManager) UpdateValue(path string, data map[string]interface{}) error {
	ref := m.client.NewRef(path)
	if err := ref.Update(m.ctx, data); err != nil {
		return fmt.Errorf("omni.realtime.update: %w", err)
	}
	return nil
}

// DeleteValue menghapus sebuah node
func (m *FirebaseRealtimeManager) DeleteValue(path string) error {
	ref := m.client.NewRef(path)
	if err := ref.Delete(m.ctx); err != nil {
		return fmt.Errorf("omni.realtime.delete: %w", err)
	}
	return nil
}
