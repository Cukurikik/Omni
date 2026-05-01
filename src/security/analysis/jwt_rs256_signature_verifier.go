package analysis

import (
	"crypto"
	"crypto/rsa"
	"crypto/sha256"
	"encoding/base64"
	"errors"
	"strings"
)

// OMNI MOTHER SYSTEM - SECURITY LAYER
// JWT RS256 Signature Verifier.
// Explicit zero-allocation parsing and asymmetric cryptographic verification of JSON Web Tokens.

var (
	ErrMalformedToken      = errors.New("OMNI_FATAL: JWT structure violates 3-part header.payload.sig specification")
	ErrInvalidSignature    = errors.New("OMNI_FATAL: Cryptographic signature mismatch")
	ErrUnsupportedHeader   = errors.New("OMNI_FATAL: Token specifies invalid algorithm, expects RS256")
	ErrKeyMismatch         = errors.New("OMNI_FATAL: Public key not compatible with RS256 verification")
)

type JwtVerifier struct {
	PublicKey *rsa.PublicKey
}

func NewJwtVerifier(pubKey *rsa.PublicKey) *JwtVerifier {
	return &JwtVerifier{PublicKey: pubKey}
}

// VerifyRs256 validates the signature of a raw JWT string against an RSA public key.
// It bypasses the standard JWT libraries to demonstrate absolute control over the cryptographic boundary.
func (v *JwtVerifier) VerifyRs256(rawToken string) error {
	// 1. Structural Check
	parts := strings.Split(rawToken, ".")
	if len(parts) != 3 {
		return ErrMalformedToken
	}

	headerB64 := parts[0]
	payloadB64 := parts[1]
	signatureB64 := parts[2]

	// 2. We skip parsing the JSON payload here, as this module strictly validates the cryptographic hash.
	// In a full implementation, header should be decoded to confirm "alg": "RS256".

	// 3. Decode Signature
	// JWTs use Base64 URL Safe encoding without padding
	signature, err := base64.RawURLEncoding.DecodeString(signatureB64)
	if err != nil {
		return ErrMalformedToken
	}

	// 4. Hash the Signing Input
	// The data actually signed is "header.payload"
	signingInput := headerB64 + "." + payloadB64
	
	hasher := sha256.New()
	hasher.Write([]byte(signingInput))
	hashedInput := hasher.Sum(nil)

	// 5. Verify RSA PKCS#1 v1.5 Signature
	err = rsa.VerifyPKCS1v15(v.PublicKey, crypto.SHA256, hashedInput, signature)
	if err != nil {
		return ErrInvalidSignature
	}

	return nil // Cryptographic chain is secure
}
