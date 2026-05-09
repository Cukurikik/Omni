package network_gocore

type ChimeraHealthCheck struct {
	IsHealthy bool
}

func (h *ChimeraHealthCheck) Check() bool {
	return h.IsHealthy
}

