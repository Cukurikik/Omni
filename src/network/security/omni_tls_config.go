package security

// omni_tls_config.go — Strict TLS 1.3 Configuration
// Layer: Network / Go
//
// Generates secure TLS configurations tailored strictly to modern
// OMNI security requirements (TLS 1.3 only, strong cipher suites). Zero mock.

import (
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"os"
)

// OmniTLSBuilder helps construct secure tls.Config instances
type OmniTLSBuilder struct {
	config *tls.Config
}

// NewOmniTLSBuilder initializes the builder enforcing TLS 1.3
func NewOmniTLSBuilder() *OmniTLSBuilder {
	return &OmniTLSBuilder{
		config: &tls.Config{
			MinVersion:               tls.VersionTLS13,
			CurvePreferences:         []tls.CurveID{tls.CurveP521, tls.CurveP384, tls.X25519},
			PreferServerCipherSuites: true,
			CipherSuites: []uint16{
				tls.TLS_AES_256_GCM_SHA384,
				tls.TLS_CHACHA20_POLY1305_SHA256,
				tls.TLS_AES_128_GCM_SHA256,
			},
		},
	}
}

// LoadServerCertificates loads the public cert and private key for the server.
func (b *OmniTLSBuilder) LoadServerCertificates(certFile, keyFile string) error {
	cert, err := tls.LoadX509KeyPair(certFile, keyFile)
	if err != nil {
		return fmt.Errorf("failed to load TLS key pair: %w", err)
	}
	b.config.Certificates = []tls.Certificate{cert}
	return nil
}

// SetupMutualTLS sets up mTLS by requiring client certificates verified against a specific CA.
func (b *OmniTLSBuilder) SetupMutualTLS(caCertFile string) error {
	caCert, err := os.ReadFile(caCertFile)
	if err != nil {
		return fmt.Errorf("failed to read CA certificate: %w", err)
	}

	caCertPool := x509.NewCertPool()
	if !caCertPool.AppendCertsFromPEM(caCert) {
		return fmt.Errorf("failed to append CA certificate to pool")
	}

	b.config.ClientCAs = caCertPool
	b.config.ClientAuth = tls.RequireAndVerifyClientCert
	return nil
}

// SetupClientTrust loads the root CA pool for a client to verify the server.
func (b *OmniTLSBuilder) SetupClientTrust(caCertFile string) error {
	caCert, err := os.ReadFile(caCertFile)
	if err != nil {
		return fmt.Errorf("failed to read CA certificate: %w", err)
	}

	caCertPool := x509.NewCertPool()
	if !caCertPool.AppendCertsFromPEM(caCert) {
		return fmt.Errorf("failed to append CA certificate to pool")
	}

	b.config.RootCAs = caCertPool
	return nil
}

// Build returns the finalized, secure TLS configuration.
func (b *OmniTLSBuilder) Build() *tls.Config {
	return b.config
}
