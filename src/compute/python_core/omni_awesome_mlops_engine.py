"""
OMNI Awesome MLOps Engine
=========================
Production-grade abstraction inspired by kelvins/awesome-mlops.
Provides a strict taxonomy structure and dependency graph validation
for MLOps lifecycle components (Data Ops, Model Ops, Dev Ops).

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Set


# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class AwesomeMLOpsError(Exception):
    """Base error for Awesome MLOps engine."""

@dataclass(frozen=True)
class Ok:
    """Monadic Ok result type."""
    value: Any

@dataclass(frozen=True)
class Err:
    """Monadic Err result type."""
    error: str

Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. MODELS & TAXONOMY
# ---------------------------------------------------------------------------

@dataclass
class MLOpsTool:
    """Production-grade M L Ops Tool component."""
    id: str
    name: str
    phase: str  # e.g. "data_engineering", "model_training", "deployment", "monitoring"
    description: str
    categories: List[str]


@dataclass
class MLOpsPipelineDef:
    """Production-grade M L Ops Pipeline Def component."""
    name: str
    tools: List[str]  # Ordered list of tool IDs
    is_valid: bool = False
    validation_messages: List[str] = field(default_factory=list)


class MLOpsTaxonomy:
    """Manages the registry and searching of MLOps tools."""
    
    def __init__(self):
        """Initialize MLOpsTaxonomy."""
        self.tools: Dict[str, MLOpsTool] = {}
        # Core phases for validation
        self.valid_phases = ["data_engineering", "model_training", "deployment", "monitoring", "feature_store"]

    def register_tool(self, tool: MLOpsTool) -> Result:
        """Execute register tool operation for MLOpsTaxonomy."""
        if tool.phase not in self.valid_phases:
            return Err(f"Phase '{tool.phase}' is not a recognized MLOps phase.")
        if tool.id in self.tools:
            return Err(f"Tool with ID '{tool.id}' already exists.")
            
        self.tools[tool.id] = tool
        return Ok(True)

    def search_by_phase(self, phase: str) -> Result:
        """Execute search by phase operation for MLOpsTaxonomy."""
        if phase not in self.valid_phases:
            return Err(f"Phase '{phase}' is not a recognized MLOps phase.")
            
        found = [t for t in self.tools.values() if t.phase == phase]
        return Ok(found)


class PipelineValidator:
    """Validates the architectural soundness of an MLOps string of tools."""
    
    def __init__(self, taxonomy: MLOpsTaxonomy):
        """Initialize PipelineValidator."""
        self.taxonomy = taxonomy
        
        # Expected phase flow for standard training-to-serving pipeline
        self.standard_flow = ["data_engineering", "model_training", "deployment", "monitoring"]

    def validate_pipeline(self, pipeline: MLOpsPipelineDef) -> Result:
        """Validate pipeline."""
        if not pipeline.tools:
            return Err("Pipeline has no tools defined.")
            
        phases_present = []
        messages = []
        is_valid = True
        
        for tool_id in pipeline.tools:
            if tool_id not in self.taxonomy.tools:
                return Err(f"Tool ID '{tool_id}' not found in taxonomy.")
            tool = self.taxonomy.tools[tool_id]
            phases_present.append(tool.phase)
            
        # Check standard flow logic (simplified Directed Acyclic mapping)
        # e.g., you shouldn't have deployment BEFORE model_training logically
        # if both exist.
        
        flow_indices = []
        for p in phases_present:
            if p in self.standard_flow:
                flow_indices.append(self.standard_flow.index(p))
                
        # Check monotonicity
        if flow_indices != sorted(flow_indices):
            is_valid = False
            messages.append("Pipeline phase order violates standard DAG flow (e.g., deployment before training).")
            
        if "monitoring" in phases_present and "deployment" not in phases_present:
            # Maybe okay, but a warning
            messages.append("Warning: Monitoring phase exists without Deployment phase in pipeline.")
            
        pipeline.is_valid = is_valid
        pipeline.validation_messages = messages
        
        return Ok(pipeline)


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniAwesomeMLOpsEngine:
    """
    Production Engine for MLOps Taxonomy and Graph Validation.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-awesome-mlops"

    def __init__(self):
        """Initialize OmniAwesomeMLOpsEngine."""
        self.taxonomy = MLOpsTaxonomy()
        
    def seed_default_tools(self) -> None:
        """Seeds common tools into the knowledge graph."""
        self.taxonomy.register_tool(MLOpsTool("dvc", "DVC", "data_engineering", "Data Version Control", ["versioning"]))
        self.taxonomy.register_tool(MLOpsTool("feast", "Feast", "feature_store", "Feature Store", ["data"]))
        self.taxonomy.register_tool(MLOpsTool("mlflow", "MLflow", "model_training", "Experiment Tracking", ["tracking", "registry"]))
        self.taxonomy.register_tool(MLOpsTool("zenml", "ZenML", "model_training", "MLOps Orchestration", ["orchestration"]))
        self.taxonomy.register_tool(MLOpsTool("seldon", "Seldon Core", "deployment", "Model Serving", ["serving", "kubernetes"]))
        self.taxonomy.register_tool(MLOpsTool("evidently", "Evidently AI", "monitoring", "Model Monitoring", ["observability"]))
        self.taxonomy.register_tool(MLOpsTool("prometheus", "Prometheus", "monitoring", "Metrics", ["metrics"]))

    def get_validator(self) -> PipelineValidator:
        """Performs get validator operation for OmniAwesomeMLOpsEngine."""
        return PipelineValidator(self.taxonomy)

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniAwesomeMLOpsEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "registered_tools": len(self.taxonomy.tools),
            "status": "operational",
        }
