// OMNI Database Layer: Cypher Knowledge Graph Schema
// Defines the foundational structure for OMNI's multi-modal knowledge storage.
// Enforces strict constraint schemas.

// 1. Core Concept Nodes
CREATE CONSTRAINT omni_concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE;
CREATE INDEX omni_concept_name IF NOT EXISTS FOR (c:Concept) ON (c.name);

// 2. Transformer Architecture Nodes
CREATE CONSTRAINT omni_model_id IF NOT EXISTS FOR (m:Model) REQUIRE m.id IS UNIQUE;
CREATE INDEX omni_model_type IF NOT EXISTS FOR (m:Model) ON (m.architecture_type);

// 3. Inference Run Tracking
CREATE CONSTRAINT omni_inference_job IF NOT EXISTS FOR (j:InferenceJob) REQUIRE j.job_id IS UNIQUE;

// Initialization Query for the graph structure
MERGE (omni:System {name: "OMNI_MOTHER", version: "3.0.0"})
MERGE (tft:Model {id: "tft_01", architecture_type: "TemporalFusionTransformer", source: "aryan-jadon/Regression-Loss-Functions-in-Time-Series-Forecasting-Tensorflow"})
MERGE (wechsel:Model {id: "wechsel_01", architecture_type: "CrossLingualTransfer", source: "CPJKU/wechsel"})
MERGE (pipegoose:System {name: "Pipegoose_4D", type: "ParallelismEngine"})

// Relate concepts
MERGE (omni)-[:MANAGES]->(tft)
MERGE (omni)-[:MANAGES]->(wechsel)
MERGE (omni)-[:ORCHESTRATES]->(pipegoose)
MERGE (pipegoose)-[:ACCELERATES]->(tft)

// Zero-Mock Knowledge Retrieval Query Template
// MATCH (s:System)-[:MANAGES]->(m:Model)
// WHERE s.name = "OMNI_MOTHER"
// RETURN m.id, m.architecture_type
