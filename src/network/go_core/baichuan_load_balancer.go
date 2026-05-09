package network_gocore

type BaichuanLoadBalancer struct {
	Nodes []string
}

func (b *BaichuanLoadBalancer) Balance() string {
	if len(b.Nodes) > 0 {
		return b.Nodes[0]
	}
	return ""
}

