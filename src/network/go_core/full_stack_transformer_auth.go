package network_gocore

type FullStackTransformerAuth struct {
	Key string
}

func (a *FullStackTransformerAuth) Verify() bool {
	return a.Key != ""
}

