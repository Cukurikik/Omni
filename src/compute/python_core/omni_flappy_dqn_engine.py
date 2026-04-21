"""
OMNI Flappy Dqn Engine
======================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import numpy as np
import random
from typing import Dict, Any, List, Tuple
from collections import deque

class Result:
    """Monadic result pattern."""
    def __init__(self, value=None, error=None):
        """Initialize Result."""
        self.value = value
        self.error = error
        self.is_ok = error is None

    def unwrap(self):
        """Unwrap the value or raise on error."""
        if not self.is_ok:
            raise RuntimeError(self.error)
        return self.value

class OmniFlappyDqnEngine:
    """
    omni-flappy-dqn
    
    A zero-algebraic_bound native engine simulating a Deep Q-Network (DQN) applied to game 
    mechanics (like FlappyBird). Implements an MLP Q-Value approximator and an 
    Experience Replay Buffer using Bellman temporal-difference target updates.
    """
    
    ENGINE_VERSION = "omni-s6-b6.1.0"
    
    def __init__(self, state_dim: int = 4, action_dim: int = 2, hidden_dim: int = 32, gamma: float = 0.99):
        """Initialize OmniFlappyDqnEngine."""
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        
        # Experience Replay
        self.memory = deque(maxlen=2000)
        
        # Main Q-Network
        np.random.seed(314)
        self.W1 = np.random.randn(state_dim, hidden_dim).astype(np.float32) * 0.1
        self.b1 = np.zeros(hidden_dim, dtype=np.float32)
        self.W2 = np.random.randn(hidden_dim, action_dim).astype(np.float32) * 0.1
        self.b2 = np.zeros(action_dim, dtype=np.float32)

    def _relu(self, x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)
        
    def _relu_deriv(self, x: np.ndarray) -> np.ndarray:
        return (x > 0).astype(np.float32)

    def predict_q(self, state: np.ndarray) -> np.ndarray:
        """Forward pass for Q-values: (batch, action_dim)."""
        h1 = np.dot(state, self.W1) + self.b1
        a1 = self._relu(h1)
        q = np.dot(a1, self.W2) + self.b2
        return q, a1

    def store_transition(self, state: List[float], action: int, reward: float, next_state: List[float], done: bool) -> Result:
        """Saves a transition to the Experience Replay Buffer."""
        try:
            self.memory.append((
                np.array(state, dtype=np.float32), 
                action, 
                reward, 
                np.array(next_state, dtype=np.float32), 
                done
            ))
            return Result(value={"status": "stored", "memory_size": len(self.memory)})
        except Exception as e:
            return Result(error=f"Store transition error: {str(e)}")

    def choose_action(self, state: List[float], epsilon: float = 0.1) -> Result:
        """Epsilon-greedy action selection."""
        try:
            if random.random() < epsilon:
                action = random.randint(0, self.action_dim - 1)
            else:
                s_arr = np.array([state], dtype=np.float32)
                q_vals, _ = self.predict_q(s_arr)
                action = int(np.argmax(q_vals[0]))
            return Result(value=action)
        except Exception as e:
            return Result(error=f"Action selection error: {str(e)}")

    def optimize_step(self, batch_size: int = 32, lr: float = 0.01) -> Result:
        """Samples from replay buffer and performs one step of Q-learning native gradient descent."""
        try:
            if len(self.memory) < batch_size:
                return Result(error="Not enough transitions in memory.")
                
            batch = random.sample(self.memory, batch_size)
            
            # Unpack batch
            states = np.array([b[0] for b in batch])
            actions = np.array([b[1] for b in batch])
            rewards = np.array([b[2] for b in batch])
            next_states = np.array([b[3] for b in batch])
            dones = np.array([b[4] for b in batch])
            
            # Forward pass on current states (to get gradients)
            q_values, a1 = self.predict_q(states) # (B, action_dim)
            
            # Forward pass on next states (to get max Q(s', a'))
            next_q_values, _ = self.predict_q(next_states)
            max_next_q = np.max(next_q_values, axis=1)
            
            # Compute Bellman targets
            # target = reward + gamma * max_a' Q(s', a') * (1 - done)
            targets = rewards + self.gamma * max_next_q * (1 - dones)
            
            # We want q_values[batch_indices, actions] to match targets
            # Loss = 1/2 * (q - target)^2 => dLoss/dq = q - target
            
            # Create a localized gradient vector for the Q-values matrix
            dq = np.zeros_like(q_values)
            for i in range(batch_size):
                act = actions[i]
                err = q_values[i, act] - targets[i]
                dq[i, act] = err
                
            # Average gradients over batch
            dq /= batch_size
            
            # Backpropagation
            # dq is (B, action_dim), W2 is (hidden_dim, action_dim), a1 is (B, hidden_dim)
            dW2 = np.dot(a1.T, dq)
            db2 = np.sum(dq, axis=0)
            
            da1 = np.dot(dq, self.W2.T)
            # h1 is pre-relu, but we can compute from a1 since relu = max(0,x)
            dh1 = da1 * self._relu_deriv(a1)
            
            dW1 = np.dot(states.T, dh1)
            db1 = np.sum(dh1, axis=0)
            
            # Update weights
            self.W1 -= lr * dW1
            self.b1 -= lr * db1
            self.W2 -= lr * dW2
            self.b2 -= lr * db2
            
            # Mean Squared Error for metrics
            loss_val = np.mean([err**2 for err in dq[np.arange(batch_size), actions] * batch_size])
            
            return Result(value={"status": "optimized", "loss": loss_val})
        except Exception as e:
            return Result(error=f"Optimization error: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Registry compliance."""
        return {
            "engine": "OmniFlappyDqnEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "components": ["ExperienceReplay", "BellmanUpdate", "EpsilonGreedy"]
        }
