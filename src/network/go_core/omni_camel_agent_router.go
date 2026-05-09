// Omni CAMEL Agent Router (Go)
// Ref: camel-ai/multi-agent-streamlit-ui
package network_gocore

type AgentMessage struct {
	From    string
	To      string
	Content string
	Role    string
}

func RouteMessage(msg *AgentMessage) string {
	order := []string{"planner", "assistant", "critic", "user_proxy"}
	for i, r := range order {
		if r == msg.Role {
			return order[(i+1)%len(order)]
		}
	}
	return "assistant"
}

