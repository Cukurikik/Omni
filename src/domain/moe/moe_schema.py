"""
moe_schema.py — GraphQL Schema for MoE Model Management
Layer: Domain / API — MoE Schema-First Contract

Defines the GraphQL API schema for MoE model management:
model registration, expert configuration, inference endpoints,
monitoring queries, and admin mutations.
"""

# This file defines the schema as Python classes to be used with
# Strawberry, Ariadne, or Graphene — framework-agnostic type definitions.

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class ExpertStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LOADING = "LOADING"
    ERROR = "ERROR"
    PRUNED = "PRUNED"


class ShardHealth(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    MAINTENANCE = "MAINTENANCE"


class RoutingStrategy(Enum):
    TOP_K = "TOP_K"
    SWITCH = "SWITCH"
    HASH = "HASH"
    EXPERT_CHOICE = "EXPERT_CHOICE"


class QuantizationMethod(Enum):
    NONE = "NONE"
    GPTQ_4BIT = "GPTQ_4BIT"
    AWQ_4BIT = "AWQ_4BIT"
    SMOOTHQUANT_INT8 = "SMOOTHQUANT_INT8"
    EXPERT_AWARE = "EXPERT_AWARE"


@dataclass
class ExpertConfig:
    """Configuration for a single expert."""
    expert_id: int
    hidden_dim: int
    ff_dim: int
    activation: str = "silu"
    dropout: float = 0.0
    status: ExpertStatus = ExpertStatus.ACTIVE
    device_id: int = 0
    quantization: QuantizationMethod = QuantizationMethod.NONE
    parameter_count: int = 0
    memory_mb: float = 0.0


@dataclass
class RouterConfig:
    """Configuration for the MoE router."""
    routing_strategy: RoutingStrategy = RoutingStrategy.TOP_K
    top_k: int = 2
    num_experts: int = 8
    capacity_factor: float = 1.25
    noise_std: float = 0.1
    load_balance_weight: float = 0.01
    z_loss_weight: float = 1e-4
    jitter_noise: float = 0.01


@dataclass
class MoEModelConfig:
    """Full MoE model configuration."""
    model_id: str
    model_name: str
    version: str = "1.0.0"
    hidden_dim: int = 768
    num_layers: int = 12
    num_heads: int = 12
    vocab_size: int = 32000
    max_seq_len: int = 2048
    router: RouterConfig = field(default_factory=RouterConfig)
    experts: List[ExpertConfig] = field(default_factory=list)
    total_parameters: int = 0
    active_parameters: int = 0


@dataclass
class ExpertUtilization:
    """Runtime utilization stats for an expert."""
    expert_id: int
    tokens_processed: int
    utilization_pct: float
    avg_weight: float
    avg_latency_ms: float
    cache_hit_rate: float


@dataclass
class ShardInfo:
    """Information about an expert shard deployment."""
    shard_id: int
    host: str
    port: int
    expert_range: List[int]  # [start, end)
    health: ShardHealth
    load_factor: float
    pending_requests: int
    memory_used_mb: float
    memory_total_mb: float


@dataclass
class InferenceInput:
    """Input for model inference."""
    input_ids: List[int]
    max_tokens: int = 128
    temperature: float = 1.0
    top_k: int = 50
    top_p: float = 0.9
    stream: bool = False


@dataclass
class InferenceOutput:
    """Output from model inference."""
    request_id: str
    output_ids: List[int]
    output_text: str
    expert_utilization: List[ExpertUtilization]
    latency_ms: float
    tokens_per_sec: float
    total_tokens: int
    load_balance_loss: float


@dataclass
class LoadBalanceReport:
    """Aggregated load balance statistics."""
    timestamp: str
    num_experts: int
    cv_squared: float
    max_utilization: float
    min_utilization: float
    entropy: float
    per_expert: List[ExpertUtilization]


@dataclass
class PruneRequest:
    """Request to prune experts from a model."""
    model_id: str
    prune_ratio: float = 0.25
    method: str = "usage"  # usage, sensitivity, combined
    min_experts: int = 2
    distill_after_prune: bool = True


@dataclass
class PruneResult:
    """Result of expert pruning."""
    model_id: str
    experts_before: int
    experts_after: int
    pruned_expert_ids: List[int]
    accuracy_before: float
    accuracy_after: float
    memory_saved_mb: float


@dataclass
class QuantizeRequest:
    """Request to quantize model experts."""
    model_id: str
    method: QuantizationMethod
    calibration_samples: int = 512
    per_expert: bool = True


@dataclass
class QuantizeResult:
    """Result of expert quantization."""
    model_id: str
    method: QuantizationMethod
    bits: int
    size_before_mb: float
    size_after_mb: float
    perplexity_before: float
    perplexity_after: float


# GraphQL Schema Definition (SDL format for documentation)
SCHEMA_SDL = """
type Query {
  model(id: ID!): MoEModel
  models: [MoEModel!]!
  expert(modelId: ID!, expertId: Int!): Expert
  shards(modelId: ID!): [Shard!]!
  loadBalanceReport(modelId: ID!): LoadBalanceReport!
  metrics(modelId: ID!): ModelMetrics!
}

type Mutation {
  registerModel(input: RegisterModelInput!): MoEModel!
  updateRouter(modelId: ID!, config: RouterConfigInput!): RouterConfig!
  pruneExperts(input: PruneInput!): PruneResult!
  quantizeModel(input: QuantizeInput!): QuantizeResult!
  scaleExperts(modelId: ID!, numExperts: Int!): MoEModel!
  inference(modelId: ID!, input: InferenceInput!): InferenceOutput!
}

type Subscription {
  expertUtilization(modelId: ID!): ExpertUtilization!
  shardHealth(modelId: ID!): Shard!
  inferenceMetrics(modelId: ID!): InferenceMetrics!
}

type MoEModel {
  id: ID!
  name: String!
  version: String!
  config: ModelConfig!
  experts: [Expert!]!
  shards: [Shard!]!
  metrics: ModelMetrics!
}

type Expert {
  id: Int!
  status: ExpertStatus!
  config: ExpertConfig!
  utilization: ExpertUtilization!
}

type Shard {
  id: Int!
  host: String!
  port: Int!
  expertRange: [Int!]!
  health: ShardHealth!
  loadFactor: Float!
}

enum ExpertStatus { ACTIVE INACTIVE LOADING ERROR PRUNED }
enum ShardHealth { HEALTHY DEGRADED UNHEALTHY MAINTENANCE }
enum RoutingStrategy { TOP_K SWITCH HASH EXPERT_CHOICE }
enum QuantizationMethod { NONE GPTQ_4BIT AWQ_4BIT SMOOTHQUANT_INT8 EXPERT_AWARE }
"""
