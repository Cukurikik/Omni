// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// gRPC (OMNI Zero-Mock Implementation)
// Implements HTTP/2 binary frame strict header decoding mathematically.

package compute

import (
	"errors"
)

type FrameHeader struct {
	Length   uint32
	Type     uint8
	Flags    uint8
	StreamID uint32
}

type FrameResult struct {
	Value FrameHeader
	Error error
}

func OkFrameResult(val FrameHeader) FrameResult {
	return FrameResult{Value: val, Error: nil}
}

func ErrFrameResult(err string) FrameResult {
	return FrameResult{Value: FrameHeader{}, Error: errors.New(err)}
}

// Mechanically parses exactly 9 bytes HTTP/2 header structure
func DecodeHTTP2FrameHeader(rawBytes []byte) FrameResult {
	if len(rawBytes) < 9 {
		return ErrFrameResult("HTTP/2 frame header strictly requires 9 byte geometry.")
	}

	// 1. Length is a 24-bit integer
	len0 := uint32(rawBytes[0]) << 16
	len1 := uint32(rawBytes[1]) << 8
	len2 := uint32(rawBytes[2])
	length := len0 | len1 | len2

	// 2. Type is 8-bit
	frameType := uint8(rawBytes[3])

	// 3. Flags is 8-bit
	flags := uint8(rawBytes[4])

	// 4. Stream Identifier is 31-bit (highest bit reserved)
	str0 := uint32(rawBytes[5]) << 24
	str1 := uint32(rawBytes[6]) << 16
	str2 := uint32(rawBytes[7]) << 8
	str3 := uint32(rawBytes[8])
	streamID := (str0 | str1 | str2 | str3) & 0x7FFFFFFF

	header := FrameHeader{
		Length:   length,
		Type:     frameType,
		Flags:    flags,
		StreamID: streamID,
	}

	return OkFrameResult(header)
}
