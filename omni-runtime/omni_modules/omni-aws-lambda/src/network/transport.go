package omni_aws_lambda

import (
	"context"
	"net"
	"time"
	"fmt"
	"crypto/tls"
)

type TransportLayer struct {
	Addr      string
	TLS       bool
	KeepAlive time.Duration
	conn      net.Conn
}

type TransportConfig struct {
	Address     string
	UseTLS      bool
	KeepAlive   time.Duration
	DialTimeout time.Duration
	CertFile    string
	KeyFile     string
}

func NewTransportLayer(cfg TransportConfig) *TransportLayer {
	return &TransportLayer{Addr: cfg.Address, TLS: cfg.UseTLS, KeepAlive: cfg.KeepAlive}
}

func (t *TransportLayer) Connect(ctx context.Context) error {
	dialer := &net.Dialer{Timeout: 10 * time.Second, KeepAlive: t.KeepAlive}
	var err error
	if t.TLS {
		t.conn, err = tls.DialWithDialer(dialer, "tcp", t.Addr, &tls.Config{InsecureSkipVerify: false})
	} else {
		t.conn, err = dialer.DialContext(ctx, "tcp", t.Addr)
	}
	if err != nil { return fmt.Errorf("omni-aws-lambda: transport connect: %w", err) }
	return nil
}

func (t *TransportLayer) Send(data []byte) (int, error) {
	if t.conn == nil { return 0, fmt.Errorf("omni-aws-lambda: not connected") }
	return t.conn.Write(data)
}

func (t *TransportLayer) Recv(buf []byte) (int, error) {
	if t.conn == nil { return 0, fmt.Errorf("omni-aws-lambda: not connected") }
	return t.conn.Read(buf)
}

func (t *TransportLayer) Close() error {
	if t.conn != nil { return t.conn.Close() }
	return nil
}