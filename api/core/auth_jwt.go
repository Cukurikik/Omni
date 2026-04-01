package core

import (
	"errors"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

// GenerateToken menciptakan Paspor Digital untuk User
func GenerateToken(userID string) (string, error) {
	if AppConfig == nil || AppConfig.Security.SessionSecret == "" {
		return "", errors.New("SessionSecret is not configured in AppConfig")
	}

	jwtSecret := []byte(AppConfig.Security.SessionSecret)

	claims := jwt.MapClaims{
		"user_id": userID,
		"exp":     time.Now().Add(time.Hour * 24).Unix(), // Berlaku 24 Jam
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtSecret)
}

// VerifyToken mengecek apakah Paspor tersebut asli atau palsu
func VerifyToken(tokenString string) (jwt.MapClaims, error) {
	if AppConfig == nil || AppConfig.Security.SessionSecret == "" {
		return nil, errors.New("SessionSecret is not configured in AppConfig")
	}

	jwtSecret := []byte(AppConfig.Security.SessionSecret)

	token, err := jwt.Parse(tokenString, func(t *jwt.Token) (interface{}, error) {
		// Pastikan metode penandatanganan sesuai HMAC
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, errors.New("unexpected signing method")
		}
		return jwtSecret, nil
	})

	if err != nil {
		return nil, err
	}

	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		return claims, nil
	}

	return nil, errors.New("invalid token")
}
