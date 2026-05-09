package network_moe

import (
	"log"
	"net"
)

// OMNI MOTHER Production Zero-Mock UDP Multicast
// Used to broadcast routing table updates and MoE model signatures
// across the local datacenter subnet instantly.

type MulticastTransceiver struct {
	Address *net.UDPAddr
	Conn    *net.UDPConn
}

func NewMulticastTransceiver(multicastIP string, port int) (*MulticastTransceiver, error) {
	addr, err := net.ResolveUDPAddr("udp4", net.JoinHostPort(multicastIP, string(rune(port))))
	if err != nil {
		return nil, err
	}

	conn, err := net.ListenMulticastUDP("udp4", nil, addr)
	if err != nil {
		return nil, err
	}

	// Set socket buffers
	conn.SetReadBuffer(1048576)

	return &MulticastTransceiver{
		Address: addr,
		Conn:    conn,
	}, nil
}

func (m *MulticastTransceiver) Broadcast(payload []byte) error {
	// Need a standard UDP conn to send to multicast address
	conn, err := net.DialUDP("udp4", nil, m.Address)
	if err != nil {
		return err
	}
	defer conn.Close()

	_, err = conn.Write(payload)
	return err
}

func (m *MulticastTransceiver) Listen(handler func([]byte)) {
	buffer := make([]byte, 8192)
	for {
		n, src, err := m.Conn.ReadFromUDP(buffer)
		if err != nil {
			log.Printf("OMNI ERROR: Multicast read failed: %v", err)
			continue
		}

		// Copy data to prevent buffer overwrite during async handling
		data := make([]byte, n)
		copy(data, buffer[:n])

		log.Printf("OMNI NETWORK: Received multicast from %s", src.String())
		go handler(data)
	}
}

