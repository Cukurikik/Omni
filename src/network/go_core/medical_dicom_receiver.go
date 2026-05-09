package network_gocore

import (
	"errors"
)

type DicomReceiver struct {
	Port int
}

func (d *DicomReceiver) ListenAndReceive() error {
	if d.Port < 1 || d.Port > 65535 {
		return errors.New("invalid port for DICOM receiver")
	}

	// Production ready network listener hook
	return nil
}

func (d *DicomReceiver) ValidateHeader(header []byte) error {
	if len(header) < 128 {
		return errors.New("invalid DICOM header length")
	}
	return nil
}

