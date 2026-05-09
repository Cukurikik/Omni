package network_http

// omni_http1_parser.go — Zero-Allocation HTTP/1.1 Parser
// Layer: Network / HTTP
// Inspired by: fasthttp
//
// Implements a raw byte-slice HTTP/1.1 parser. Avoids Go garbage collection
// overhead by reading directly from a pre-allocated buffer and returning
// slice references instead of allocating new strings. Zero mock.

import (
	"bytes"
	"errors"
)

var (
	ErrIncompleteRequest = errors.New("incomplete HTTP request")
	ErrBadRequest        = errors.New("bad HTTP request format")
)

var (
	strSpace = []byte(" ")
	strCRLF  = []byte("\r\n")
	strColon = []byte(":")
)

// OmniHTTPRequest points to slices within the original buffer
type OmniHTTPRequest struct {
	Method  []byte
	URI     []byte
	Version []byte
	Headers [][2][]byte // Array of [Key, Value] pairs
	Body    []byte
}

func NewOmniHTTPRequest() *OmniHTTPRequest {
	return &OmniHTTPRequest{
		Headers: make([][2][]byte, 0, 16), // Pre-allocate capacity for 16 headers
	}
}

// ParseRequest parses an HTTP/1.1 request from the raw buffer.
// Returns the number of bytes consumed.
func (req *OmniHTTPRequest) ParseRequest(buf []byte) (int, error) {
	req.Headers = req.Headers[:0] // Reset headers slice length without reallocating

	// Find end of headers (double CRLF)
	headerEnd := bytes.Index(buf, []byte("\r\n\r\n"))
	if headerEnd == -1 {
		return 0, ErrIncompleteRequest
	}

	// 1. Parse Request Line (Method URI Version)
	lineEnd := bytes.Index(buf, strCRLF)
	if lineEnd == -1 || lineEnd > headerEnd {
		return 0, ErrBadRequest
	}

	reqLine := buf[:lineEnd]

	firstSpace := bytes.Index(reqLine, strSpace)
	if firstSpace == -1 {
		return 0, ErrBadRequest
	}
	req.Method = reqLine[:firstSpace]

	secondSpace := bytes.Index(reqLine[firstSpace+1:], strSpace)
	if secondSpace == -1 {
		return 0, ErrBadRequest
	}
	secondSpace += firstSpace + 1

	req.URI = reqLine[firstSpace+1 : secondSpace]
	req.Version = reqLine[secondSpace+1:]

	// 2. Parse Headers
	headersBuf := buf[lineEnd+2 : headerEnd]

	for len(headersBuf) > 0 {
		idx := bytes.Index(headersBuf, strCRLF)
		var hLine []byte
		if idx == -1 {
			hLine = headersBuf
			headersBuf = nil
		} else {
			hLine = headersBuf[:idx]
			headersBuf = headersBuf[idx+2:]
		}

		colonIdx := bytes.Index(hLine, strColon)
		if colonIdx != -1 {
			k := hLine[:colonIdx]

			// Trim leading spaces from value
			vStart := colonIdx + 1
			for vStart < len(hLine) && hLine[vStart] == ' ' {
				vStart++
			}
			v := hLine[vStart:]

			req.Headers = append(req.Headers, [2][]byte{k, v})
		}
	}

	// Body starts after the double CRLF
	bodyStart := headerEnd + 4
	req.Body = buf[bodyStart:]

	// Note: True implementation needs Content-Length / Transfer-Encoding checks
	// to determine exact body bounds. This consumes the rest of the buffer.

	return len(buf), nil
}

