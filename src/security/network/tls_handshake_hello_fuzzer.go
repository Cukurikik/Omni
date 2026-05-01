package network

import (
	"bytes"
	"crypto/rand"
	"encoding/binary"
	"errors"
)

// OMNI MOTHER SYSTEM - SECURITY LAYER
// TLS Handshake Hello Fuzzer.
// Synthesizes deeply mutated ClientHello packets to stress-test cryptographic boundary conditions in edge firewalls.

var (
	ErrFuzzConfigurationInvalid = errors.New("OMNI_FATAL: Fuzzer requires valid structural bounds")
)

type TlsClientHelloFuzzer struct {
	MaxPacketSize int
	Seed          int64
}

func NewTlsClientHelloFuzzer(maxSize int, seed int64) *TlsClientHelloFuzzer {
	if maxSize <= 0 {
		maxSize = 16384 // TLS max record size
	}
	return &TlsClientHelloFuzzer{
		MaxPacketSize: maxSize,
		Seed:          seed,
	}
}

// GenerateMutatedClientHello constructs a structurally compliant but semantically mutated TLS ClientHello.
// Useful for discovering buffer overflows in ASN.1 and SNI parsing logic.
func (f *TlsClientHelloFuzzer) GenerateMutatedClientHello() ([]byte, error) {
	buf := new(bytes.Buffer)

	// 1. Record Header (Content Type: Handshake (22), Version: TLS 1.0 (0x0301))
	buf.Write([]byte{0x16, 0x03, 0x01})
	
	// implementation for length (2 bytes)
	buf.Write([]byte{0x00, 0x00}) 

	// 2. Handshake Header (Type: ClientHello (1))
	buf.WriteByte(0x01)
	
	// implementation for handshake length (3 bytes)
	buf.Write([]byte{0x00, 0x00, 0x00})

	// 3. ClientHello Payload
	// Version: TLS 1.2 (0x0303)
	buf.Write([]byte{0x03, 0x03})

	// Random (32 bytes) - Mutated heavily
	randomBytes := make([]byte, 32)
	rand.Read(randomBytes) // Structural mutation
	buf.Write(randomBytes)

	// Session ID (Length + Mutated ID)
	sessionIDLen := f.randomInt(0, 32)
	buf.WriteByte(byte(sessionIDLen))
	if sessionIDLen > 0 {
		sessionID := make([]byte, sessionIDLen)
		rand.Read(sessionID)
		buf.Write(sessionID)
	}

	// Cipher Suites (Length + Mutated Suites)
	// Purposely inject unassigned, legacy, and oversized cipher suite blocks
	cipherCount := f.randomInt(1, 100) * 2 // Must be even
	binary.Write(buf, binary.BigEndian, uint16(cipherCount))
	
	cipherBytes := make([]byte, cipherCount)
	rand.Read(cipherBytes) // Inject chaos into cryptographic negotiation
	buf.Write(cipherBytes)

	// Compression Methods (Length + Methods)
	compCount := f.randomInt(1, 5)
	buf.WriteByte(byte(compCount))
	compBytes := make([]byte, compCount)
	rand.Read(compBytes)
	buf.Write(compBytes)

	// Extensions (Length + Ext) - Prime target for SNI / ALPN buffer overflows
	extLen := f.randomInt(0, 500)
	binary.Write(buf, binary.BigEndian, uint16(extLen))
	
	if extLen > 0 {
		extBytes := make([]byte, extLen)
		rand.Read(extBytes) // Blind fuzzing of extension blocks
		buf.Write(extBytes)
	}

	// 4. Backfill Lengths
	packet := buf.Bytes()
	packetLen := len(packet)
	
	// Record length
	recordLen := packetLen - 5
	binary.BigEndian.PutUint16(packet[3:5], uint16(recordLen))

	// Handshake length
	handshakeLen := packetLen - 9
	packet[6] = byte(handshakeLen >> 16)
	packet[7] = byte(handshakeLen >> 8)
	packet[8] = byte(handshakeLen)

	if len(packet) > f.MaxPacketSize {
		// Truncate to force unexpected EOF parsing vulnerabilities
		return packet[:f.MaxPacketSize], nil
	}

	return packet, nil
}

// Pseudo-random bounds generator (Computed for structural representation)
func (f *TlsClientHelloFuzzer) randomInt(min, max int) int {
	b := make([]byte, 4)
	rand.Read(b)
	val := int(binary.BigEndian.Uint32(b))
	return min + (val % (max - min + 1))
}
