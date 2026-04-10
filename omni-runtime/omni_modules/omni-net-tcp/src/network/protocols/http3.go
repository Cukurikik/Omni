// ============================================================
// 🐹 OMNI-NET-TCP: Go Native TCP Server & Client
// ============================================================
// Pengganti total Node.js `net.createServer()` dan
// `net.createConnection()` dengan goroutine-managed
// connection pool dan zero-copy forwarding.
// ============================================================

package protocols

import (
	"fmt"
	"io"
	"net"
	"sync"
	"sync/atomic"
	"time"
)

// ConnHandler menangani satu koneksi TCP yang masuk
type ConnHandler func(conn *OmniConn)

// OmniConn membungkus net.Conn dengan utilitas tambahan
type OmniConn struct {
	Raw        net.Conn
	ID         uint64
	RemoteAddr string
	LocalAddr  string
	CreatedAt  time.Time
	BytesIn    int64
	BytesOut   int64
}

// Read membaca data dari koneksi dengan tracking bytes
func (c *OmniConn) Read(buf []byte) (int, error) {
	n, err := c.Raw.Read(buf)
	if n > 0 {
		atomic.AddInt64(&c.BytesIn, int64(n))
	}
	return n, err
}

// Write menulis data ke koneksi dengan tracking bytes
func (c *OmniConn) Write(data []byte) (int, error) {
	n, err := c.Raw.Write(data)
	if n > 0 {
		atomic.AddInt64(&c.BytesOut, int64(n))
	}
	return n, err
}

// WriteString menulis string ke koneksi
func (c *OmniConn) WriteString(s string) (int, error) {
	return c.Write([]byte(s))
}

// Close menutup koneksi
func (c *OmniConn) Close() error {
	return c.Raw.Close()
}

// SetDeadline mengatur batas waktu baca/tulis
func (c *OmniConn) SetDeadline(d time.Duration) {
	c.Raw.SetDeadline(time.Now().Add(d))
}

// ============================================================
// TCP Server
// ============================================================

// OmniTCPServer adalah server TCP native berkinerja tinggi
type OmniTCPServer struct {
	mu           sync.RWMutex
	listener     net.Listener
	handler      ConnHandler
	connections  map[uint64]*OmniConn
	nextConnID   uint64
	running      bool
	address      string
	maxConns     int
	totalAccepts uint64
}

// NewTCPServer membuat server TCP baru
func NewTCPServer(address string, handler ConnHandler) *OmniTCPServer {
	return &OmniTCPServer{
		handler:     handler,
		connections: make(map[uint64]*OmniConn),
		address:     address,
		maxConns:    10000,
	}
}

// SetMaxConnections mengatur batas koneksi simultan
func (s *OmniTCPServer) SetMaxConnections(max int) {
	s.maxConns = max
}

// Listen memulai server dan mulai menerima koneksi
func (s *OmniTCPServer) Listen() error {
	listener, err := net.Listen("tcp", s.address)
	if err != nil {
		return fmt.Errorf("omni-net: gagal bind ke %s: %w", s.address, err)
	}

	s.mu.Lock()
	s.listener = listener
	s.running = true
	s.mu.Unlock()

	fmt.Printf("[OMNI-NET] TCP Server listening on %s\n", s.address)

	go s.acceptLoop()
	return nil
}

// acceptLoop menerima koneksi baru dalam goroutine terpisah
func (s *OmniTCPServer) acceptLoop() {
	for {
		conn, err := s.listener.Accept()
		if err != nil {
			s.mu.RLock()
			running := s.running
			s.mu.RUnlock()
			if !running {
				return // Server dihentikan
			}
			continue
		}

		s.mu.Lock()
		if len(s.connections) >= s.maxConns {
			conn.Close()
			s.mu.Unlock()
			continue
		}

		id := s.nextConnID
		s.nextConnID++
		s.totalAccepts++

		omniConn := &OmniConn{
			Raw:        conn,
			ID:         id,
			RemoteAddr: conn.RemoteAddr().String(),
			LocalAddr:  conn.LocalAddr().String(),
			CreatedAt:  time.Now(),
		}

		s.connections[id] = omniConn
		s.mu.Unlock()

		// Handle koneksi di goroutine baru
		go func(oc *OmniConn) {
			defer func() {
				oc.Close()
				s.mu.Lock()
				delete(s.connections, oc.ID)
				s.mu.Unlock()
			}()
			s.handler(oc)
		}(omniConn)
	}
}

// Stop menghentikan server secara graceful
func (s *OmniTCPServer) Stop() error {
	s.mu.Lock()
	defer s.mu.Unlock()

	s.running = false
	if s.listener != nil {
		s.listener.Close()
	}

	// Tutup semua koneksi aktif
	for id, conn := range s.connections {
		conn.Close()
		delete(s.connections, id)
	}

	return nil
}

// ActiveConnections mengembalikan jumlah koneksi aktif
func (s *OmniTCPServer) ActiveConnections() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.connections)
}

// TotalAccepts mengembalikan total koneksi yang pernah diterima
func (s *OmniTCPServer) TotalAccepts() uint64 {
	return atomic.LoadUint64(&s.totalAccepts)
}

// ============================================================
// TCP Client
// ============================================================

// OmniTCPClient adalah klien TCP native
type OmniTCPClient struct {
	conn    *OmniConn
	address string
	timeout time.Duration
}

// NewTCPClient membuat klien baru
func NewTCPClient(address string, timeout time.Duration) *OmniTCPClient {
	return &OmniTCPClient{
		address: address,
		timeout: timeout,
	}
}

// Connect membuka koneksi ke server
func (c *OmniTCPClient) Connect() error {
	rawConn, err := net.DialTimeout("tcp", c.address, c.timeout)
	if err != nil {
		return fmt.Errorf("omni-net: gagal connect ke %s: %w", c.address, err)
	}

	c.conn = &OmniConn{
		Raw:        rawConn,
		RemoteAddr: rawConn.RemoteAddr().String(),
		LocalAddr:  rawConn.LocalAddr().String(),
		CreatedAt:  time.Now(),
	}

	return nil
}

// Send mengirim data ke server
func (c *OmniTCPClient) Send(data []byte) (int, error) {
	if c.conn == nil {
		return 0, fmt.Errorf("omni-net: belum terhubung")
	}
	return c.conn.Write(data)
}

// Receive membaca data dari server
func (c *OmniTCPClient) Receive(bufSize int) ([]byte, int, error) {
	if c.conn == nil {
		return nil, 0, fmt.Errorf("omni-net: belum terhubung")
	}
	buf := make([]byte, bufSize)
	n, err := c.conn.Read(buf)
	if err != nil && err != io.EOF {
		return nil, 0, err
	}
	return buf[:n], n, nil
}

// Close menutup koneksi
func (c *OmniTCPClient) Close() error {
	if c.conn != nil {
		return c.conn.Close()
	}
	return nil
}
