// OMNI Gym Q-Learning Engine — Compute Layer (Python)
// Absorbing openai/gym (Gymnasium) state/action spaces
// Temporal Difference Bellman Equation logic

from typing import List, Dict, Any, Tuple
import random

class GymError(Exception):
    pass

class OmniGymQlearningBellman:
    def __init__(self, states: int, actions: int, alpha: float=0.1, gamma: float=0.9):
        self.num_states = states
        self.num_actions = actions
        self.learning_rate = alpha
        self.discount_factor = gamma
        self.q_table = [[0.0 for _ in range(actions)] for _ in range(states)]
        self.episodes_trained = 0

    def get_action_epsilon_greedy(self, state: int, epsilon: float) -> Tuple[bool, int, str]:
        try:
            if state < 0 or state >= self.num_states:
                raise GymError(f"State out of bounds: {state}")

            if random.random() < epsilon:
                # Explore
                return True, random.randint(0, self.num_actions - 1), ""
            else:
                # Exploit
                row = self.q_table[state]
                max_val = max(row)
                best_action = row.index(max_val)
                return True, best_action, ""
        except GymError as e:
            return False, -1, str(e)
        except Exception as e:
            return False, -1, f"System Panic: {e}"

    def update_q_value(self, state: int, action: int, reward: float, next_state: int, done: bool) -> Tuple[bool, str]:
        """
        Bellman Equation: Q(s,a) = Q(s,a) + alpha * [R + gamma * max Q(s', a') - Q(s,a)]
        """
        try:
            if state < 0 or state >= self.num_states or next_state < 0 or next_state >= self.num_states:
                raise GymError("State index violation.")
            if action < 0 or action >= self.num_actions:
                raise GymError("Action index violation.")

            self.episodes_trained += 1

            target = reward
            if not done:
                best_next_q = max(self.q_table[next_state])
                target += self.discount_factor * best_next_q

            td_error = target - self.q_table[state][action]
            self.q_table[state][action] += self.learning_rate * td_error

            return True, ""
        except GymError as e:
            return False, str(e)
        except Exception as e:
            return False, f"System Panic: {e}"

    def get_q_table_dump(self) -> List[List[float]]:
        # Returns current trained optimal bounds
        return self.q_table

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniGymQlearningBellman",
            "episodes": self.episodes_trained,
            "status": "Operational"
        }
