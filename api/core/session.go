package core

import (
	"crypto/rand"
	"encoding/hex"
	"net/http"
	"sync"
	"time"
)

type SessionData struct {
	UserID    string
	Role      string
	ExpiresAt int64
}

// Memory aman untuk Concurrency tingkat tinggi
var (
	sessionStore = make(map[string]*SessionData)
	sessionMutex sync.RWMutex
)

// GenerateSession membuat token kriptografi aman
func GenerateSession(userID string, role string) string {
	bytes := make([]byte, 32)
	rand.Read(bytes)
	token := hex.EncodeToString(bytes)

	sessionMutex.Lock()
	sessionStore[token] = &SessionData{
		UserID:    userID,
		Role:      role,
		ExpiresAt: time.Now().Add(24 * time.Hour).Unix(),
	}
	sessionMutex.Unlock()

	return token
}

// GetSession mengambil sesi dan memvalidasi waktu kadaluarsa
func GetSession(r *http.Request) *SessionData {
	cookie, err := r.Cookie("omni_session")
	if err != nil {
		return nil
	}

	sessionMutex.RLock()
	data, exists := sessionStore[cookie.Value]
	sessionMutex.RUnlock()

	if !exists || time.Now().Unix() > data.ExpiresAt {
		return nil // Sesi tidak valid atau kadaluarsa
	}
	return data
}
