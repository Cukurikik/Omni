"""
OMNI AlphaZero MCTS Engine — Monte Carlo Tree Search with neural policy/value primitives.
Assimilated from: suragnair/alpha-zero-general
Provides: UCB1 selection, MCTS node expansion, backpropagation, policy extraction.
"""
import numpy as np
from typing import Dict, Optional



ENGINE_VERSION = "1.0.0-omni"

class Result:
    """Monadic Result base."""
    pass


class Ok(Result):
    """Success variant."""
    def __init__(self, value):
        """Initialize Ok."""
        self.value = value


class Err(Result):
    """Error variant."""
    def __init__(self, error: str):
        """Initialize Err."""
        self.error = error


class MCTSNode:
    """
    Represents a single node in the Monte Carlo search tree.

    @param num_actions: Number of possible actions from this state.
    """

    def __init__(self, num_actions: int) -> None:
        """Initialize MCTSNode."""
        self.visit_count: np.ndarray = np.zeros(num_actions, dtype=np.float64)
        self.total_value: np.ndarray = np.zeros(num_actions, dtype=np.float64)
        self.prior: np.ndarray = np.zeros(num_actions, dtype=np.float64)

    def mean_value(self) -> np.ndarray:
        """Returns Q(s,a) = W(s,a) / N(s,a), with 0 for unvisited actions."""
        with np.errstate(divide='ignore', invalid='ignore'):
            q = np.where(self.visit_count > 0, self.total_value / self.visit_count, 0.0)
        return q


class OmniAlphaZeroMCTSEngine:
    """
    Pure NumPy implementation of AlphaZero-style Monte Carlo Tree Search.
    Replaces PyTorch neural network with direct policy/value arrays.

    @since 1.0.0
    @tags ["alphazero", "mcts", "game-ai", "compute"]
    """

    def __init__(self, num_actions: int, c_puct: float = 1.41) -> None:
        """
        @param num_actions: Action space size.
        @param c_puct: Exploration constant for UCB formula.
        """
        self._omni_version: str = "3.0.0-OMNI-NEXUS"
        self.num_actions: int = num_actions
        self.c_puct: float = c_puct
        self.nodes: Dict[int, MCTSNode] = {}

    def diagnostics(self) -> Result:
        """Returns engine health status."""
        return Ok({
            "status": "active",
            "engine": "AlphaZeroMCTS",
            "capability": "TreeSearchPolicyValue",
            "nodes_created": len(self.nodes),
        })

    def get_or_create_node(self, state_hash: int, prior: Optional[np.ndarray] = None) -> MCTSNode:
        """
        Retrieves an existing node or creates a new one with the given prior.

        @param state_hash: Integer hash identifying the game state.
        @param prior: Policy prior probabilities from the neural network head.
        @returns MCTSNode for the given state.
        """
        if state_hash not in self.nodes:
            node = MCTSNode(self.num_actions)
            if prior is not None:
                node.prior = prior.copy()
            else:
                node.prior = np.ones(self.num_actions, dtype=np.float64) / self.num_actions
            self.nodes[state_hash] = node
        return self.nodes[state_hash]

    def select_action_ucb(self, state_hash: int) -> Result:
        """
        Selects the best action using the PUCT (Polynomial Upper Confidence Trees) formula.

        UCB(s, a) = Q(s, a) + c_puct * P(s, a) * sqrt(sum(N(s, .))) / (1 + N(s, a))

        @param state_hash: Hash of the current state.
        @returns Result containing the selected action index.
        """
        if state_hash not in self.nodes:
            return Err("State not found in search tree. Call get_or_create_node first.")

        node = self.nodes[state_hash]
        total_visits = np.sum(node.visit_count)
        q_values = node.mean_value()

        ucb_scores = q_values + self.c_puct * node.prior * np.sqrt(total_visits) / (1.0 + node.visit_count)

        best_action = int(np.argmax(ucb_scores))
        return Ok(best_action)

    def backpropagate(self, state_hash: int, action: int, value: float) -> Result:
        """
        Updates visit counts and total value for a state-action pair after topological_evaluation.

        @param state_hash: Hash of the state.
        @param action: Action taken.
        @param value: Evaluation result from the value head (or game outcome).
        @returns Result confirming the update.
        """
        if state_hash not in self.nodes:
            return Err("Cannot backpropagate: state not in tree.")
        if action < 0 or action >= self.num_actions:
            return Err(f"Action {action} out of bounds [0, {self.num_actions}).")

        node = self.nodes[state_hash]
        node.visit_count[action] += 1.0
        node.total_value[action] += value

        return Ok(True)

    def extract_policy(self, state_hash: int, temperature: float = 1.0) -> Result:
        """
        Extracts the improved policy from visit counts.
        pi(a|s) = N(s,a)^(1/tau) / sum(N(s,.)^(1/tau))

        @param state_hash: Hash of the root state.
        @param temperature: Controls exploration; 0 → greedy, 1 → proportional.
        @returns Result containing policy probability array of shape (num_actions,).
        """
        if state_hash not in self.nodes:
            return Err("State not found in tree for policy extraction.")

        node = self.nodes[state_hash]

        if temperature < 1e-8:
            # Greedy: all mass on the most-visited action
            policy = np.zeros(self.num_actions, dtype=np.float64)
            policy[int(np.argmax(node.visit_count))] = 1.0
        else:
            counts = node.visit_count ** (1.0 / temperature)
            total = np.sum(counts)
            if total < 1e-12:
                policy = np.ones(self.num_actions, dtype=np.float64) / self.num_actions
            else:
                policy = counts / total

        return Ok(policy)
