// OMNI Framework - Cypher Graph Schema for LLM Knowledge
// Stores relationships between different models, datasets, and architectures

// Create core nodes
CREATE CONSTRAINT ON (m:Model) ASSERT m.id IS UNIQUE;
CREATE CONSTRAINT ON (d:Dataset) ASSERT d.id IS UNIQUE;
CREATE CONSTRAINT ON (a:Architecture) ASSERT a.id IS UNIQUE;

// Insert sample architectures
CREATE (:Architecture {id: "arch_transformer", name: "Transformer", attention: "Self-Attention"});
CREATE (:Architecture {id: "arch_remixer", name: "Remixer Block", attention: "Spatial Mixing"});

// Insert sample datasets
CREATE (:Dataset {id: "ds_smashed", name: "SMASHED Transformations", modality: "text"});

// Insert sample models and relate them
CREATE (m1:Model {id: "model_finbert", name: "FinBERT", params: "110M"})
MATCH (a:Architecture {id: "arch_transformer"})
CREATE (m1)-[:USES_ARCHITECTURE]->(a);

CREATE (m2:Model {id: "model_televit", name: "TeleViT", params: "86M"})
MATCH (a:Architecture {id: "arch_transformer"})
CREATE (m2)-[:USES_ARCHITECTURE]->(a);

// Query to find all models using a specific architecture
// MATCH (m:Model)-[:USES_ARCHITECTURE]->(a:Architecture {id: "arch_transformer"})
// RETURN m.name, a.name;
