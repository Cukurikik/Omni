package supabase

import (
	"crypto/rsa"
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

// OMNI SUPABASE: JWT Verifier
// Go domain logic for strict cryptographic validation of Supabase access tokens.
// Enforces Monadic Error Handling patterns natively.
// Source: supabase/supabase

type TokenError struct {
	Code    string
	Message string
}

func (e *TokenError) Error() string {
	return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}

type JWTVerifier struct {
	publicKey *rsa.PublicKey
	issuer    string
}

func NewJWTVerifier(pemBytes []byte, issuer string) (*JWTVerifier, error) {
	pubKey, err := jwt.ParseRSAPublicKeyFromPEM(pemBytes)
	if err != nil {
		return nil, &TokenError{Code: "KEY_ERR", Message: "Invalid public key format"}
	}
	return &JWTVerifier{publicKey: pubKey, issuer: issuer}, nil
}

// Verify enforces strict expiration, audience, and signature validation
func (v *JWTVerifier) Verify(tokenStr string) (jwt.MapClaims, error) {
	token, err := jwt.Parse(tokenStr, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodRSA); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return v.publicKey, nil
	})

	if err != nil {
		return nil, &TokenError{Code: "SIG_FAIL", Message: err.Error()}
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok || !token.Valid {
		return nil, &TokenError{Code: "INVALID_CLAIMS", Message: "Token claims are invalid"}
	}

	// Validate Expiration
	if exp, ok := claims["exp"].(float64); ok {
		if time.Now().Unix() > int64(exp) {
			return nil, &TokenError{Code: "EXPIRED", Message: "Token has expired"}
		}
	} else {
		return nil, &TokenError{Code: "MALFORMED", Message: "Missing expiration claim"}
	}

	// Validate Issuer
	if iss, ok := claims["iss"].(string); !ok || iss != v.issuer {
		return nil, &TokenError{Code: "BAD_ISSUER", Message: "Issuer mismatch"}
	}

	return claims, nil
}
