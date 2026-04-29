package network

import "errors"

type VLLMEngine struct{}

func (e *VLLMEngine) AddRequest(reqId string) error {
    if reqId == "" {
        return errors.New("invalid request ID")
    }
    return nil
}
