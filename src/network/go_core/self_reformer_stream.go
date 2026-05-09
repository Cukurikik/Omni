package network_gocore

import "errors"

type ReformerStream struct {
	IsOpen bool
}

func (s *ReformerStream) SendFrame(data []byte) error {
	if !s.IsOpen {
		return errors.New("stream is closed")
	}
	if len(data) == 0 {
		return errors.New("empty frame")
	}
	return nil
}

