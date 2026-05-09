// moe_jwt_key_rotator.go — Network / Security
// Layer: Network / Gateways — Automated Zero-Downtime Key Rotation
//
// MoE inference gateways validate tenant JWTs. To prevent token hijacking,
// the cryptographic signing keys must be rotated frequently. This Go daemon
// automates a 24-hour rotation cycle using a rolling window, ensuring
// no active connection is dropped during the transition.

package network_moe

import (
	"crypto/rand"
	"crypto/rsa"
	"fmt"
	"sync"
	"time"
)

type KeySet struct {
	ActiveKey   *rsa.PrivateKey
	PreviousKey *rsa.PrivateKey // Kept for validating tokens issued just before rotation
	mu          sync.RWMutex
}

type JWTRotator struct {
	keys           *KeySet
	rotationPeriod time.Duration
}

func NewJWTRotator(periodHours int) *JWTRotator {
	rotator := &JWTRotator{
		keys:           &KeySet{},
		rotationPeriod: time.Duration(periodHours) * time.Hour,
	}

	// Initial key generation
	rotator.rotateKeys()

	fmt.Printf("[JWT Rotator] Initialized automated key rotation daemon. Period: %d hours.\n", periodHours)
	return rotator
}

func (r *JWTRotator) StartDaemon() {
	ticker := time.NewTicker(r.rotationPeriod)
	go func() {
		for range ticker.C {
			r.rotateKeys()
		}
	}()
}

func (r *JWTRotator) rotateKeys() {
	// Generate new 2048-bit RSA key
	newKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		fmt.Println("[JWT Rotator] CRITICAL ERROR: Failed to generate new RSA key.")
		return
	}

	r.keys.mu.Lock()
	defer r.keys.mu.Unlock()

	// Shift active key to previous, and set new key as active
	if r.keys.ActiveKey != nil {
		r.keys.PreviousKey = r.keys.ActiveKey
	}
	r.keys.ActiveKey = newKey

	fmt.Println("[JWT Rotator] Successfully rotated JWT cryptographic signing keys (Zero-Downtime).")

	// In production, the public key is immediately pushed to Redis/Consul so
	// authentication servers know the new valid signature.
}

// GetKeys allows the Authorizer to fetch the keys for validation safely
func (r *JWTRotator) GetKeys() (*rsa.PrivateKey, *rsa.PrivateKey) {
	r.keys.mu.RLock()
	defer r.keys.mu.RUnlock()
	return r.keys.ActiveKey, r.keys.PreviousKey
}

