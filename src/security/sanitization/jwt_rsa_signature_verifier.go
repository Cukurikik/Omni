package sanitization

import (
	"crypto"
	"crypto/rsa"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"strings"
	"time"
)

// OMNI MOTHER SYSTEM - SECURITY LAYER
// JWT RSA Signature Verifier.
// Strictly validates RS256 JSON Web Tokens without relying on external bloatware libraries.

var (
	ErrMalformedToken   = errors.New("OMNI_FATAL: Malformed JWT structure")
	ErrUnsupportedAlg   = errors.New("OMNI_FATAL: Unsupported JWT algorithm, expected RS256")
	ErrSignatureInvalid = errors.New("OMNI_FATAL: JWT cryptographic signature verification failed")
	ErrTokenExpired     = errors.New("OMNI_FATAL: JWT has expired")
)

type JwtHeader struct {
	Alg string `json:"alg"`
	Typ string `json:"typ"`
}

type JwtPayload struct {
	Sub string `json:"sub"`
	Exp int64  `json:"exp"`
	Iss string `json:"iss"`
	Aud string `json:"aud"`
}

type JwtValidator struct {
	PublicKey *rsa.PublicKey
}

func NewJwtValidator(pubKey *rsa.PublicKey) *JwtValidator {
	return &JwtValidator{PublicKey: pubKey}
}

// Verify securely decrypts and validates an RS256 token against the loaded Public Key.
func (v *JwtValidator) Verify(tokenString string) (*JwtPayload, error) {
	parts := strings.Split(tokenString, ".")
	if len(parts) != 3 {
		return nil, ErrMalformedToken
	}

	headerB64, payloadB64, signatureB64 := parts[0], parts[1], parts[2]

	// 1. Verify Header Algorithm
	headerBytes, err := base64.RawURLEncoding.DecodeString(headerB64)
	if err != nil {
		return nil, ErrMalformedToken
	}

	var header JwtHeader
	if err := json.Unmarshal(headerBytes, &header); err != nil {
		return nil, ErrMalformedToken
	}

	if header.Alg != "RS256" {
		// Strictly reject "none" or symmetric "HS256" attacks
		return nil, ErrUnsupportedAlg
	}

	// 2. Cryptographic Signature Verification
	signedData := headerB64 + "." + payloadB64
	hashed := sha256.Sum256([]byte(signedData))

	signatureBytes, err := base64.RawURLEncoding.DecodeString(signatureB64)
	if err != nil {
		return nil, ErrMalformedToken
	}

	// rsa.VerifyPKCS1v15 is constant-time and immune to timing attacks
	err = rsa.VerifyPKCS1v15(v.PublicKey, crypto.SHA256, hashed[:], signatureBytes)
	if err != nil {
		return nil, ErrSignatureInvalid
	}

	// 3. Payload Extraction and Temporal Validation
	payloadBytes, err := base64.RawURLEncoding.DecodeString(payloadB64)
	if err != nil {
		return nil, ErrMalformedToken
	}

	var payload JwtPayload
	if err := json.Unmarshal(payloadBytes, &payload); err != nil {
		return nil, ErrMalformedToken
	}

	// Exp is Unix Timestamp
	if payload.Exp > 0 {
		if time.Now().Unix() > payload.Exp {
			return nil, ErrTokenExpired
		}
	}

	return &payload, nil
}
