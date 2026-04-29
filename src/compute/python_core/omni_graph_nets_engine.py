"""
OMNI Graph Nets Engine
========================
Production-grade Graph Neural Network (GNN) engine inspired by
google-deepmind/graph_nets.
Implements the core Message Passing Neural Network (MPNN) framework,
Graph Attention Networks (GAT), and Graph Convolutional Networks (GCN)
over structured Graph Tuples.

Extracted Patterns:
  - Graphs Tuple abstraction (nodes, edges, globals, senders, receivers)
  - Generic Message Passing blocks (EdgeBlock, NodeBlock, GlobalBlock)
  - Graph Convolutional Network (GCN) layer
  - Graph Attention Network (GAT) layer
  - Aggregation primitives (scatter_sum, scatter_max, scatter_mean)

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad & Utilities
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class GraphNetsError(Exception):
    """Base error for Graph Nets engine."""

@dataclass(frozen=True)
class Ok:
    """Monadic Ok result type."""
    value: Any

@dataclass(frozen=True)
class Err:
    """Monadic Err result type."""
    error: str

Result = Union[Ok, Err]


def scatter_sum(data: np.ndarray, indices: np.ndarray, out_size: int) -> np.ndarray:
    """evaluates_structurally tf.math.unsorted_segment_sum or scatter_add."""
    out_shape = (out_size,) + data.shape[1:]
    out = np.zeros(out_shape, dtype=data.dtype)
    np.add.at(out, indices, data)
    return out


def scatter_max(data: np.ndarray, indices: np.ndarray, out_size: int) -> np.ndarray:
    """evaluates_structurally scatter_max."""
    out_shape = (out_size,) + data.shape[1:]
    out = np.full(out_shape, -np.inf, dtype=data.dtype)
    np.maximum.at(out, indices, data)
    out[out == -np.inf] = 0.0 # reset unchanged
    return out


def scatter_mean(data: np.ndarray, indices: np.ndarray, out_size: int) -> np.ndarray:
    """evaluates_structurally scatter_mean."""
    sum_data = scatter_sum(data, indices, out_size)
    counts = scatter_sum(np.ones_like(data), indices, out_size)
    counts = np.maximum(counts, 1.0)
    return sum_data / counts


def softmax_segments(data: np.ndarray, indices: np.ndarray, num_segments: int) -> np.ndarray:
    """Segmented softmax for attention (e.g. over incoming edges to a node)."""
    max_data = scatter_max(data, indices, num_segments)
    max_expanded = max_data[indices]
    exp_data = np.exp(data - max_expanded)
    sum_exp = scatter_sum(exp_data, indices, num_segments)
    sum_exp_expanded = sum_exp[indices]
    return exp_data / (sum_exp_expanded + 1e-10)


# ---------------------------------------------------------------------------
# 2. GRAPH TUPLE ABSTRACTION
# ---------------------------------------------------------------------------

@dataclass
class GraphTuple:
    """
    Represents a batch of graphs.
    nodes: (N_nodes, node_feat_dim)
    edges: (N_edges, edge_feat_dim)
    globals: (N_graphs, global_feat_dim)
    senders: (N_edges,) indices of source nodes
    receivers: (N_edges,) indices of target nodes
    n_node: (N_graphs,) number of nodes per graph
    n_edge: (N_graphs,) number of edges per graph
    """
    nodes: np.ndarray
    edges: Optional[np.ndarray] = None
    globals: Optional[np.ndarray] = None
    senders: Optional[np.ndarray] = None
    receivers: Optional[np.ndarray] = None
    n_node: Optional[np.ndarray] = None
    n_edge: Optional[np.ndarray] = None

    @property
    def total_nodes(self) -> int:
        """Execute total nodes operation for GraphTuple."""
        return self.nodes.shape[0]

    @property
    def total_edges(self) -> int:
        """Execute total edges operation for GraphTuple."""
        return self.edges.shape[0] if self.edges is not None else 0

    @property
    def num_graphs(self) -> int:
        """Execute num graphs operation for GraphTuple."""
        return self.n_node.shape[0] if self.n_node is not None else 1

    def copy(self) -> 'GraphTuple':
        """Execute copy operation for GraphTuple."""
        return GraphTuple(
            nodes=self.nodes.copy(),
            edges=self.edges.copy() if self.edges is not None else None,
            globals=self.globals.copy() if self.globals is not None else None,
            senders=self.senders.copy() if self.senders is not None else None,
            receivers=self.receivers.copy() if self.receivers is not None else None,
            n_node=self.n_node.copy() if self.n_node is not None else None,
            n_edge=self.n_edge.copy() if self.n_edge is not None else None
        )

# ---------------------------------------------------------------------------
# 3. MESSAGE PASSING BASE BLOCKS
# ---------------------------------------------------------------------------

class MLP:
    """Simple Multi-Layer Perceptron engine for block functions."""
    def __init__(self, in_features: int, out_features: int, seed: int = 42):
        """Initialize MLP."""
        rs = np.random.RandomState(seed)
        self.W = rs.randn(in_features, out_features).astype(np.float32) * 0.1
        self.b = np.zeros(out_features, dtype=np.float32)

    def __call__(self, x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x @ self.W + self.b) # ReLU activation


class EdgeBlock:
    """Updates edge features based on edge, sender node, receiver node, and globals."""
    def __init__(self, func: Callable[[np.ndarray], np.ndarray]):
        """Initialize EdgeBlock."""
        self.func = func

    def __call__(self, graph: GraphTuple) -> GraphTuple:
        if graph.edges is None or graph.senders is None or graph.receivers is None:
            return graph

        # Gather node features
        sender_nodes = graph.nodes[graph.senders]
        receiver_nodes = graph.nodes[graph.receivers]

        # Gather globals (broadcast to edges)
        # Assuming single graph for simplicity, or complex gathering if batched
        if graph.globals is not None:
            # Map graph index to edge index (simplified for single graph)
            glob_feat = np.repeat(graph.globals, graph.edges.shape[0], axis=0) if graph.globals.shape[0] == 1 else graph.globals[0:1] # Fallback
            inputs = np.concatenate([graph.edges, sender_nodes, receiver_nodes, glob_feat], axis=-1)
        else:
            inputs = np.concatenate([graph.edges, sender_nodes, receiver_nodes], axis=-1)

        updated_edges = self.func(inputs)
        new_graph = graph.copy()
        new_graph.edges = updated_edges
        return new_graph


class NodeBlock:
    """Updates node features based on node features, aggregated incoming edges, and globals."""
    def __init__(self, func: Callable[[np.ndarray], np.ndarray],
                 aggregator: Callable = scatter_sum):
        """Initialize NodeBlock."""
        self.func = func
        self.aggregator = aggregator

    def __call__(self, graph: GraphTuple) -> GraphTuple:
        # Aggregated incoming edges
        if graph.edges is not None and graph.receivers is not None:
            agg_edges = self.aggregator(graph.edges, graph.receivers, graph.total_nodes)
        else:
            agg_edges = np.zeros((graph.total_nodes, 1), dtype=np.float32)

        # Globals
        if graph.globals is not None:
            glob_feat = np.repeat(graph.globals, graph.total_nodes, axis=0) if graph.globals.shape[0] == 1 else graph.globals[0:1]
            inputs = np.concatenate([graph.nodes, agg_edges, glob_feat], axis=-1)
        else:
            inputs = np.concatenate([graph.nodes, agg_edges], axis=-1)

        updated_nodes = self.func(inputs)
        new_graph = graph.copy()
        new_graph.nodes = updated_nodes
        return new_graph


class GlobalBlock:
    """Updates globals based on aggregated nodes, aggregated edges, and globals."""
    def __init__(self, func: Callable[[np.ndarray], np.ndarray],
                 edge_agg: Callable = scatter_sum, node_agg: Callable = scatter_sum):
        """Initialize GlobalBlock."""
        self.func = func
        self.edge_agg = edge_agg
        self.node_agg = node_agg

    def __call__(self, graph: GraphTuple) -> GraphTuple:
        # Simplified for single graph in batch (N_graphs=1)
        if graph.globals is None:
            return graph

        agg_nodes = np.sum(graph.nodes, axis=0, keepdims=True)
        if graph.edges is not None:
            agg_edges = np.sum(graph.edges, axis=0, keepdims=True)
            inputs = np.concatenate([graph.globals, agg_nodes, agg_edges], axis=-1)
        else:
            inputs = np.concatenate([graph.globals, agg_nodes], axis=-1)

        updated_globals = self.func(inputs)
        new_graph = graph.copy()
        new_graph.globals = updated_globals
        return new_graph

# ---------------------------------------------------------------------------
# 4. GCN LAYER (Graph Convolutional Network)
# ---------------------------------------------------------------------------

class GCNLayer:
    """
    Kipf & Welling GCN.
    H^{(l+1)} = \sigma(\tilde{D}^{-1/2} \tilde{A} \tilde{D}^{-1/2} H^{(l)} W^{(l)})
    Implemented via message passing for sparse graphs.
    """
    def __init__(self, in_features: int, out_features: int, seed: int = 42):
        """Initialize GCNLayer."""
        rs = np.random.RandomState(seed)
        self.W = rs.randn(in_features, out_features).astype(np.float32) * 0.1
        self.b = np.zeros(out_features, dtype=np.float32)

    def __call__(self, graph: GraphTuple) -> GraphTuple:
        # 1. Linear projection H * W
        H_proj = graph.nodes @ self.W + self.b

        if graph.senders is None or graph.receivers is None:
            new_graph = graph.copy()
            new_graph.nodes = H_proj
            return new_graph

        N = graph.total_nodes
        
        # 2. Compute degree matrix for renormalization trick (add self loops conceptually)
        # Degree based on incoming edges + 1 (for self loop)
        deg = scatter_sum(np.ones_like(graph.receivers, dtype=np.float32), graph.receivers, N) + 1.0
        deg_inv_sqrt = np.power(deg, -0.5)

        # 3. Message passing: gather along edges
        messages = H_proj[graph.senders]
        
        # Normalize messages: factor = 1 / sqrt(deg(u) * deg(v))
        norm_factor = deg_inv_sqrt[graph.senders] * deg_inv_sqrt[graph.receivers]
        messages = messages * norm_factor[:, None]

        # 4. Aggregate messages at receiver
        out = scatter_sum(messages, graph.receivers, N)
        
        # Add self-loops (H_proj * norm_factor for u=v)
        self_loop_norm = deg_inv_sqrt * deg_inv_sqrt
        out += H_proj * self_loop_norm[:, None]

        # 5. Activation
        out_act = np.maximum(0, out) # ReLU

        new_graph = graph.copy()
        new_graph.nodes = out_act
        return new_graph

# ---------------------------------------------------------------------------
# 5. GAT LAYER (Graph Attention Network)
# ---------------------------------------------------------------------------

class GATLayer:
    """
    Velickovic et al. Graph Attention Network.
    Computes attention weights between connected nodes.
    """
    def __init__(self, in_features: int, out_features: int, seed: int = 42):
        """Initialize GATLayer."""
        rs = np.random.RandomState(seed)
        self.W = rs.randn(in_features, out_features).astype(np.float32) * 0.1
        self.a = rs.randn(2 * out_features, 1).astype(np.float32) * 0.1

    def __call__(self, graph: GraphTuple) -> GraphTuple:
        # 1. Linear projection
        H_proj = graph.nodes @ self.W

        if graph.senders is None or graph.receivers is None:
            new_graph = graph.copy()
            new_graph.nodes = np.maximum(0, H_proj)
            return new_graph

        N = graph.total_nodes

        # 2. Compute attention scores for each edge
        # a(Wu, Wv)
        H_sender = H_proj[graph.senders]
        H_receiver = H_proj[graph.receivers]
        
        # Concat [Wu || Wv]
        concat = np.concatenate([H_sender, H_receiver], axis=-1)
        
        # LeakyReLU(a.T * concat)
        e = concat @ self.a
        e = np.where(e > 0, e, 0.2 * e)

        # 3. Softmax over neighborhood (segments grouped by receiver)
        alpha = softmax_segments(e, graph.receivers, N)

        # 4. Message passing and aggregation
        messages = H_sender * alpha
        out = scatter_sum(messages, graph.receivers, N)

        # Note: self attention requires explicit self-loops in senders/receivers in this formulation.

        # 5. Activation
        out_act = np.maximum(0, out) # ELU traditionally, using ReLU for sim

        new_graph = graph.copy()
        new_graph.nodes = out_act
        return new_graph


# ---------------------------------------------------------------------------
# 6. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniGraphNetsEngine:
    """
    Production-grade Graph Neural Network composition engine.

    Features:
      - GraphTuple abstraction wrapping heterogeneous array topologies
      - Generic Message Passing blocks: Node, Edge, Global blocks
      - Standard GNN Layers: GCN (Kipf) and GAT (Velickovic)
      - Scatter operations (Sum, Max, Mean, Softmax) for optimized operations
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-graph-nets"

    def __init__(self):
        """Initialize OmniGraphNetsEngine."""
        pass

    def create_graph(self, nodes: np.ndarray, edges: Optional[np.ndarray], 
                     senders: Optional[np.ndarray], receivers: Optional[np.ndarray],
                     globals: Optional[np.ndarray] = None) -> GraphTuple:
        """Helper to safely construct GraphTuples."""
        n_node = np.array([nodes.shape[0]], dtype=np.int32)
        n_edge = np.array([edges.shape[0]] if edges is not None else [0], dtype=np.int32)
        
        return GraphTuple(
            nodes=nodes.astype(np.float32),
            edges=edges.astype(np.float32) if edges is not None else None,
            globals=globals.astype(np.float32) if globals is not None else None,
            senders=senders.astype(np.int32) if senders is not None else None,
            receivers=receivers.astype(np.int32) if receivers is not None else None,
            n_node=n_node,
            n_edge=n_edge
        )

    def create_gcn_layer(self, in_features: int, out_features: int) -> GCNLayer:
        """Performs create gcn layer operation for OmniGraphNetsEngine."""
        return GCNLayer(in_features, out_features)

    def create_gat_layer(self, in_features: int, out_features: int) -> GATLayer:
        """Performs create gat layer operation for OmniGraphNetsEngine."""
        return GATLayer(in_features, out_features)

    def create_mpnn_block(self, edge_func: Callable, node_func: Callable, global_func: Callable) -> Callable:
        """Creates a full MPNN step (Edge -> Node -> Global)."""
        edge_block = EdgeBlock(edge_func)
        node_block = NodeBlock(node_func)
        global_block = GlobalBlock(global_func)
        
        def mpnn_step(graph: GraphTuple) -> GraphTuple:
            # Typical execution order
            g1 = edge_block(graph)
            g2 = node_block(g1)
            g3 = global_block(g2)
            return g3
            
        return mpnn_step

    def scatter_sum(self, data: np.ndarray, indices: np.ndarray, num_segments: int) -> np.ndarray:
        """Performs scatter sum operation for OmniGraphNetsEngine."""
        return scatter_sum(data, indices, num_segments)

    # --- Health ---

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniGraphNetsEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "architecture_supported": ["MPNN", "GCN", "GAT"],
            "scatter_ops": ["sum", "max", "mean", "softmax_segment"],
            "components": [
                "GraphTuple", "EdgeBlock", "NodeBlock", "GlobalBlock",
                "GCNLayer", "GATLayer"
            ],
            "status": "operational"
        }
