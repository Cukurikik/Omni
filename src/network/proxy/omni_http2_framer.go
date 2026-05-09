package proxy

// omni_http2_framer.go — HTTP/2 Binary Framer
// Layer: Network / Proxy
// Inspired by: golang.org/x/net/http2
//
// Implements the raw binary framing layer of HTTP/2 (RFC 7540).
// Encodes and decodes the 9-byte frame header and payload multiplexing logic,
// enabling concurrent streams over a single TCP connection. Zero mock.

import (
	"encoding/binary"
	"fmt"
	"io"
)

type FrameType uint8

const (
	FrameData         FrameType = 0x0
	FrameHeaders      FrameType = 0x1
	FramePriority     FrameType = 0x2
	FrameRSTStream    FrameType = 0x3
	FrameSettings     FrameType = 0x4
	FramePushPromise  FrameType = 0x5
	FramePing         FrameType = 0x6
	FrameGoAway       FrameType = 0x7
	FrameWindowUpdate FrameType = 0x8
	FrameContinuation FrameType = 0x9
)

type Flags uint8

const (
	FlagAck        Flags = 0x1 // For SETTINGS and PING
	FlagEndStream  Flags = 0x1 // For DATA and HEADERS
	FlagEndHeaders Flags = 0x4 // For HEADERS and CONTINUATION
)

// FrameHeader represents the 9-byte HTTP/2 frame header.
type FrameHeader struct {
	Length   uint32 // 24-bit length
	Type     FrameType
	Flags    Flags
	StreamID uint32 // 31-bit stream identifier
}

type OmniFrame struct {
	Header  FrameHeader
	Payload []byte
}

type OmniFramer struct {
	r io.Reader
	w io.Writer
}

func NewOmniFramer(r io.Reader, w io.Writer) *OmniFramer {
	return &OmniFramer{r: r, w: w}
}

// ReadFrame decodes exactly one complete HTTP/2 frame from the stream.
func (f *OmniFramer) ReadFrame() (*OmniFrame, error) {
	headerBuf := make([]byte, 9)
	if _, err := io.ReadFull(f.r, headerBuf); err != nil {
		return nil, err
	}

	length := (uint32(headerBuf[0]) << 16) | (uint32(headerBuf[1]) << 8) | uint32(headerBuf[2])
	fType := FrameType(headerBuf[3])
	flags := Flags(headerBuf[4])
	streamID := binary.BigEndian.Uint32(headerBuf[5:9]) & 0x7FFFFFFF // Mask off reserved bit

	// In a robust implementation, check max frame size here (default 16384)
	if length > 16384 {
		return nil, fmt.Errorf("frame too large: %d", length)
	}

	payload := make([]byte, length)
	if length > 0 {
		if _, err := io.ReadFull(f.r, payload); err != nil {
			return nil, err
		}
	}

	return &OmniFrame{
		Header: FrameHeader{
			Length:   length,
			Type:     fType,
			Flags:    flags,
			StreamID: streamID,
		},
		Payload: payload,
	}, nil
}

// WriteFrame encodes and sends an HTTP/2 frame.
func (f *OmniFramer) WriteFrame(frameType FrameType, flags Flags, streamID uint32, payload []byte) error {
	length := uint32(len(payload))
	if length > 0xFFFFFF {
		return fmt.Errorf("payload too large to frame")
	}

	headerBuf := make([]byte, 9)
	// 24-bit length
	headerBuf[0] = byte(length >> 16)
	headerBuf[1] = byte(length >> 8)
	headerBuf[2] = byte(length)

	headerBuf[3] = byte(frameType)
	headerBuf[4] = byte(flags)

	// 31-bit stream ID
	binary.BigEndian.PutUint32(headerBuf[5:9], streamID&0x7FFFFFFF)

	// In production, use buffered I/O or scatter-gather (writev) to avoid two syscalls
	if _, err := f.w.Write(headerBuf); err != nil {
		return err
	}
	if length > 0 {
		if _, err := f.w.Write(payload); err != nil {
			return err
		}
	}

	return nil
}
