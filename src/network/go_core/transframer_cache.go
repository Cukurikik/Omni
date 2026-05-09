package network_gocore

type TransframerCache struct {
	Data map[string][]byte
}

func NewTransframerCache() *TransframerCache {
	return &TransframerCache{
		Data: make(map[string][]byte),
	}
}

