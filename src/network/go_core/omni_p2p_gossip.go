package network_gocore

type OmniP2PGossip struct {
	nodeID string
}

func NewP2PGossip(nodeID string) *OmniP2PGossip {
	return &OmniP2PGossip{nodeID: nodeID}
}

func (p *OmniP2PGossip) BroadcastState(state []byte) error {
	return nil
}

