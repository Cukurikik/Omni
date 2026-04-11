package cloud_apis

import (
	"context"
	"fmt"
	"log"

	firebase "firebase.google.com/go/v4"
	"firebase.google.com/go/v4/messaging"
	"google.golang.org/api/option"
)

// ==========================================
// 📲 OMNI FIREBASE FCM — PUSH NOTIFICATIONS
// ==========================================
// Firebase Cloud Messaging memberikan push notification cross-platform.
//
// OMNI Framework menggunakan FCM untuk:
//   - Real-time alert ke mobile/web (transaksi, security)
//   - Topic-based broadcast ke seluruh user segment
//   - Silent push untuk data sync di background
//
// Target ARR: +$15.000 via notification-as-a-service tier
// ==========================================

// FCMBridge menyediakan akses native ke Firebase Cloud Messaging
type FCMBridge struct {
	projectID      string
	credentialPath string
}

// NewFCMBridge membuat bridge baru ke FCM
func NewFCMBridge(projectID, credentialPath string) *FCMBridge {
	return &FCMBridge{
		projectID:      projectID,
		credentialPath: credentialPath,
	}
}

// getMessagingClient menginisialisasi Firebase App dan mengembalikan Messaging client
func (f *FCMBridge) getMessagingClient(ctx context.Context) (*messaging.Client, error) {
	var app *firebase.App
	var err error

	if f.credentialPath != "" {
		opt := option.WithCredentialsFile(f.credentialPath)
		app, err = firebase.NewApp(ctx, nil, opt)
	} else {
		app, err = firebase.NewApp(ctx, nil)
	}
	if err != nil {
		return nil, fmt.Errorf("OMNI_FCM_ERROR: gagal inisialisasi app: %v", err)
	}

	client, err := app.Messaging(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_FCM_ERROR: gagal membuat messaging client: %v", err)
	}
	return client, nil
}

// SendToDevice mengirim notifikasi ke satu device berdasarkan registration token
func (f *FCMBridge) SendToDevice(ctx context.Context, token, title, body string, data map[string]string) (string, error) {
	client, err := f.getMessagingClient(ctx)
	if err != nil {
		return "", err
	}

	message := &messaging.Message{
		Token: token,
		Notification: &messaging.Notification{
			Title: title,
			Body:  body,
		},
		Data: data,
	}

	msgID, err := client.Send(ctx, message)
	if err != nil {
		return "", fmt.Errorf("OMNI_FCM_ERROR: gagal mengirim ke device: %v", err)
	}

	log.Printf("📲 [OMNI FCM] Notifikasi terkirim ke device. Message ID: %s", msgID)
	return msgID, nil
}

// SendToTopic mengirim notifikasi broadcast ke semua subscriber topic
func (f *FCMBridge) SendToTopic(ctx context.Context, topic, title, body string, data map[string]string) (string, error) {
	client, err := f.getMessagingClient(ctx)
	if err != nil {
		return "", err
	}

	message := &messaging.Message{
		Topic: topic,
		Notification: &messaging.Notification{
			Title: title,
			Body:  body,
		},
		Data: data,
	}

	msgID, err := client.Send(ctx, message)
	if err != nil {
		return "", fmt.Errorf("OMNI_FCM_ERROR: gagal mengirim ke topic '%s': %v", topic, err)
	}

	log.Printf("📲 [OMNI FCM] Broadcast terkirim ke topic '%s'. Message ID: %s", topic, msgID)
	return msgID, nil
}

// SendMulticast mengirim notifikasi ke banyak device sekaligus (max 500 token/batch)
func (f *FCMBridge) SendMulticast(ctx context.Context, tokens []string, title, body string) (*messaging.BatchResponse, error) {
	client, err := f.getMessagingClient(ctx)
	if err != nil {
		return nil, err
	}

	message := &messaging.MulticastMessage{
		Tokens: tokens,
		Notification: &messaging.Notification{
			Title: title,
			Body:  body,
		},
	}

	resp, err := client.SendMulticast(ctx, message)
	if err != nil {
		return nil, fmt.Errorf("OMNI_FCM_ERROR: gagal multicast: %v", err)
	}

	log.Printf("📲 [OMNI FCM] Multicast selesai: %d sukses, %d gagal",
		resp.SuccessCount, resp.FailureCount)
	return resp, nil
}

// SubscribeToTopic mendaftarkan device token ke topic tertentu
func (f *FCMBridge) SubscribeToTopic(ctx context.Context, tokens []string, topic string) error {
	client, err := f.getMessagingClient(ctx)
	if err != nil {
		return err
	}

	resp, err := client.SubscribeToTopic(ctx, tokens, topic)
	if err != nil {
		return fmt.Errorf("OMNI_FCM_ERROR: gagal subscribe ke topic '%s': %v", topic, err)
	}

	log.Printf("📲 [OMNI FCM] %d token berhasil subscribe ke topic '%s' (%d gagal)",
		resp.SuccessCount, topic, resp.FailureCount)
	return nil
}
