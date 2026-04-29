import numpy as np

class TraxRLAgent:
    def __init__(self, state_dim, action_dim):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.weights = np.random.randn(state_dim, action_dim) * 0.1

    def select_action(self, state):
        logits = np.dot(state, self.weights)
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)
        return np.argmax(probs)

if __name__ == "__main__":
    agent = TraxRLAgent(4, 2)
    state = np.array([0.5, -0.2, 0.1, 0.9])
    action = agent.select_action(state)
    print(f"Selected action: {action}")
