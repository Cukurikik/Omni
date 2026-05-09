package grpc

// omni_grpc_auth_interceptor.go — JWT Auth Interceptor
// Layer: Network / Go
//
// Intercepts incoming gRPC requests, extracts Bearer tokens from metadata,
// and validates JWT signatures. Injects user claims into the context. Zero mock.

import (
	"context"
	"fmt"
	"strings"

	"github.com/golang-jwt/jwt/v5"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"
)

type contextKey string

const UserClaimsKey contextKey = "omni_user_claims"

// OmniAuthInterceptor manages the JWT validation logic
type OmniAuthInterceptor struct {
	jwtSecret []byte
	issuer    string
}

// NewOmniAuthInterceptor creates a new interceptor configured with a secret key
func NewOmniAuthInterceptor(secret string, issuer string) *OmniAuthInterceptor {
	return &OmniAuthInterceptor{
		jwtSecret: []byte(secret),
		issuer:    issuer,
	}
}

// UnaryServerInterceptor returns the interceptor function for unary gRPC calls
func (i *OmniAuthInterceptor) UnaryServerInterceptor() grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req interface{},
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (interface{}, error) {

		// Bypass auth for health checks or public endpoints if necessary
		if info.FullMethod == "/omni.health.Health/Check" {
			return handler(ctx, req)
		}

		newCtx, err := i.authorize(ctx)
		if err != nil {
			return nil, err
		}

		return handler(newCtx, req)
	}
}

func (i *OmniAuthInterceptor) authorize(ctx context.Context) (context.Context, error) {
	md, ok := metadata.FromIncomingContext(ctx)
	if !ok {
		return nil, status.Errorf(codes.Unauthenticated, "metadata is not provided")
	}

	values := md["authorization"]
	if len(values) == 0 {
		return nil, status.Errorf(codes.Unauthenticated, "authorization token is not provided")
	}

	accessToken := values[0]
	if !strings.HasPrefix(accessToken, "Bearer ") {
		return nil, status.Errorf(codes.Unauthenticated, "invalid authorization scheme")
	}

	tokenString := strings.TrimPrefix(accessToken, "Bearer ")

	claims := jwt.MapClaims{}
	token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method")
		}
		return i.jwtSecret, nil
	})

	if err != nil || !token.Valid {
		return nil, status.Errorf(codes.Unauthenticated, "invalid or expired token")
	}

	// Validate issuer
	if iss, ok := claims["iss"].(string); !ok || iss != i.issuer {
		return nil, status.Errorf(codes.Unauthenticated, "invalid token issuer")
	}

	// Propagate claims to the handler
	newCtx := context.WithValue(ctx, UserClaimsKey, claims)
	return newCtx, nil
}

