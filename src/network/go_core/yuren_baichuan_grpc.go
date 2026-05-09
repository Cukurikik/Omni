package network_gocore

import "errors"

type BaichuanGrpcService struct {
	Port int
}

func (s *BaichuanGrpcService) Start() error {
	if s.Port == 0 {
		return errors.New("port not configured")
	}
	return nil
}

