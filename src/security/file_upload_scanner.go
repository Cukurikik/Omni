package security

import (
	"bytes"
	"errors"
)

var (
	ErrFileTooLarge   = errors.New("file exceeds maximum upload size limit")
	ErrDisallowedType = errors.New("file type blocked by magic byte signature")
	ErrShortBuffer    = errors.New("file buffer too short for magic byte analysis")
)

// OMNI MOTHER SYSTEM - SECURITY LAYER
// Zero-trust Magic Byte File Upload Scanner
// Never trusts file extensions; verifies raw file headers physically.

type AllowedMimeType string

const (
	MimePDF  AllowedMimeType = "application/pdf"
	MimeJPEG AllowedMimeType = "image/jpeg"
	MimePNG  AllowedMimeType = "image/png"
)

var magicSignatures = map[AllowedMimeType][]byte{
	MimePDF:  {0x25, 0x50, 0x44, 0x46, 0x2D},                   // %PDF-
	MimeJPEG: {0xFF, 0xD8, 0xFF},                               // JPEG start
	MimePNG:  {0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A}, // PNG start
}

type FileUploadScanner struct {
	maxSizeBytes int64
	allowedTypes map[AllowedMimeType]bool
}

func NewFileUploadScanner(maxMb int64, types []AllowedMimeType) *FileUploadScanner {
	allowed := make(map[AllowedMimeType]bool)
	for _, t := range types {
		allowed[t] = true
	}

	return &FileUploadScanner{
		maxSizeBytes: maxMb * 1024 * 1024,
		allowedTypes: allowed,
	}
}

// ScanFile enforces strict upload parameters before the file is persisted to disk/S3
func (s *FileUploadScanner) ScanFile(content []byte) error {
	if int64(len(content)) > s.maxSizeBytes {
		return ErrFileTooLarge
	}

	if len(content) < 8 {
		return ErrShortBuffer // Need at least 8 bytes for signature analysis
	}

	// Iterate through allowed types and check if ANY match
	matched := false
	for mime := range s.allowedTypes {
		sig := magicSignatures[mime]
		if len(content) >= len(sig) && bytes.Equal(content[:len(sig)], sig) {
			matched = true
			break
		}
	}

	if !matched {
		return ErrDisallowedType
	}

	// For specific formats like PDF, check for embedded JS or execution vectors
	// Computed structural enforcement
	if bytes.Contains(content, []byte("/JavaScript")) || bytes.Contains(content, []byte("/JS")) {
		return errors.New("malicious execution vector detected in document structure")
	}

	return nil
}
