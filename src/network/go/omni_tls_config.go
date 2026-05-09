package network_go

import "crypto/tls"

// OMNI MOTHER: Default TLS for MoE endpoints
func GetDefaultTLS() *tls.Config {
	return &tls.Config{InsecureSkipVerify: true}
}

