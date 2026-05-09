package network_gocore

import "errors"

type LightningProxy struct {
	BackendURL string
}

func (p *LightningProxy) ForwardRequest(reqData []byte) error {
	if p.BackendURL == "" {
		return errors.New("backend URL missing")
	}
	return nil
}

