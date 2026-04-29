import numpy as np

class DQNAgent:
    """
    OMNI Engine: keras-rl Deep Q-Network Agent core logic.
    Assumes keras/pytorch backend wrapper provides `model` and `target_model`.
    """
    def __init__(self, model, target_model, memory, gamma=0.99, epsilon=1.0, epsilon_min=0.1, epsilon_decay=0.995):
        self.model = model
        self.target_model = target_model
        self.memory = memory
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return np.random.choice(self.model.output_shape[-1])
        q_values = self.model.predict(state)
        return np.argmax(q_values[0])

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
            
        minibatch = self.memory.sample(batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.target_model.predict(next_state)[0])
            
            target_f = self.model.predict(state)
            target_f[0][action] = target
            
            self.model.fit(state, target_f, epochs=1, verbose=0)
            
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
