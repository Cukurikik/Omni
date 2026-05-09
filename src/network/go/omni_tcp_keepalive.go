package network_go

import (
	"log"
	"net"
	"time"
)

// OMNI MOTHER: TCP Keepalive Tuner (Production Grade)

func EnableAggressiveKeepalive(conn *net.TCPConn) error {
	err := conn.SetKeepAlive(true)
	if err != nil {
		return err
	}

	// Drop connection quickly if peer vanishes (critical for MoE cluster sync)
	err = conn.SetKeepAlivePeriod(5 * time.Second)
	if err != nil {
		return err
	}

	log.Printf("[OMNI TCP] Aggressive Keepalive enabled for %s", conn.RemoteAddr().String())
	return nil
}

