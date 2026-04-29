package serverlessllm

import "errors"

type OmniResult struct {
	Value interface{}
	Error error
}

type InstancePool struct {
	MaxInstances int
}

func (p *InstancePool) RouteRequest(modelID string, currentLoad float64) OmniResult {
	if modelID == "" {
		return OmniResult{Value: nil, Error: errors.New("Model ID cannot be empty")}
	}

	if currentLoad > 0.95 {
		// Serverless auto-scaling trigger logic
		scaledInstances := int(float64(p.MaxInstances) * 1.5)
		return OmniResult{
			Value: map[string]interface{}{
				"action":         "scale_up",
				"new_capacity":   scaledInstances,
				"routed_node_id": "node-standby-1",
			},
			Error: nil,
		}
	}

	return OmniResult{
		Value: map[string]interface{}{
			"action":         "route",
			"routed_node_id": "node-active-1",
		},
		Error: nil,
	}
}
