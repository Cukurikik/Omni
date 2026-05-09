// @omni-layer Database | @omni-lang Cypher | @omni-batch 18 | @omni-semester 16
// @omni-description Neo4j knowledge graph for transformer model lineage,
// entity relationships, and knowledge editing audit trail.

// === Schema Constraints ===
CREATE CONSTRAINT model_id_unique IF NOT EXISTS FOR (m:Model) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT edit_id_unique IF NOT EXISTS FOR (ed:KnowledgeEdit) REQUIRE ed.id IS UNIQUE;
CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;

// === Indexes ===
CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name);
CREATE INDEX model_type IF NOT EXISTS FOR (m:Model) ON (m.type);
CREATE INDEX edit_timestamp IF NOT EXISTS FOR (ed:KnowledgeEdit) ON (ed.timestamp);

// === Model Registry ===
CREATE (tempo:Model {id: 'tempo-forecaster', type: 'timeseries', version: '1.0.0',
    d_model: 768, n_heads: 12, params_billion: 0.125, created: datetime()})
CREATE (hiformer:Model {id: 'hiformer-seg', type: 'segmentation', version: '1.0.0',
    d_model: 256, n_heads: 8, params_billion: 0.085, created: datetime()})
CREATE (vidclass:Model {id: 'video-classifier', type: 'video', version: '1.0.0',
    d_model: 768, n_heads: 12, params_billion: 0.300, created: datetime()})
CREATE (bertner:Model {id: 'bert-ner', type: 'ner', version: '1.0.0',
    d_model: 768, n_heads: 12, params_billion: 0.110, created: datetime()})

// === Model Lineage ===
CREATE (bert:Model {id: 'bert-base', type: 'foundation', version: '1.0.0',
    d_model: 768, n_heads: 12, params_billion: 0.110, created: datetime()})
CREATE (gpt2:Model {id: 'gpt2-medium', type: 'foundation', version: '1.0.0',
    d_model: 1024, n_heads: 16, params_billion: 0.345, created: datetime()})

MATCH (parent:Model {id: 'bert-base'}), (child:Model {id: 'bert-ner'})
CREATE (child)-[:FINE_TUNED_FROM {dataset: 'CoNLL-2003', epochs: 5}]->(parent);

MATCH (parent:Model {id: 'gpt2-medium'}), (child:Model {id: 'tempo-forecaster'})
CREATE (child)-[:ADAPTED_FROM {method: 'prompt-tuning', domain: 'time-series'}]->(parent);

// === Entity Knowledge Graph ===
MATCH (m:Model {id: 'bert-ner'})
CREATE (e1:Entity {id: 'ent-001', name: 'Albert Einstein', type: 'PER', confidence: 0.98})
CREATE (e2:Entity {id: 'ent-002', name: 'Princeton University', type: 'ORG', confidence: 0.95})
CREATE (e3:Entity {id: 'ent-003', name: 'Germany', type: 'LOC', confidence: 0.99})
CREATE (e1)-[:AFFILIATED_WITH {since: 1933}]->(e2)
CREATE (e1)-[:BORN_IN]->(e3)
CREATE (e1)-[:EXTRACTED_BY]->(m);

// === Knowledge Edit Audit ===
CREATE (edit1:KnowledgeEdit {id: 'edit-001', subject: 'Albert Einstein',
    relation: 'works_at', old_object: 'ETH Zurich', new_object: 'Princeton University',
    timestamp: datetime(), applied_to_layer: 8, verified: true})
MATCH (u:User {id: 'curator-01'}), (ed:KnowledgeEdit {id: 'edit-001'}), (m:Model {id: 'bert-ner'})
CREATE (u)-[:PERFORMED]->(ed)
CREATE (ed)-[:APPLIED_TO]->(m);

// === Queries ===
// Find model lineage
// MATCH path = (m:Model)-[:FINE_TUNED_FROM|ADAPTED_FROM*]->(base:Model)
// WHERE m.id = 'bert-ner'
// RETURN path;

// Find all entities extracted by a model
// MATCH (e:Entity)-[:EXTRACTED_BY]->(m:Model {id: 'bert-ner'})
// RETURN e.name, e.type, e.confidence ORDER BY e.confidence DESC;

// Audit knowledge edits
// MATCH (u:User)-[:PERFORMED]->(ed:KnowledgeEdit)-[:APPLIED_TO]->(m:Model)
// RETURN u.id, ed.subject, ed.relation, ed.new_object, m.id, ed.timestamp
// ORDER BY ed.timestamp DESC LIMIT 100;
