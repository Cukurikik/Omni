// OMNI Framework - Cypher Queries for MoE Graph Analytics
// Analyzes the structural relationship between incoming prompts and expert activation

// Create Constraints
CREATE CONSTRAINT ON (p:Prompt) ASSERT p.hash IS UNIQUE;
CREATE CONSTRAINT ON (e:ExpertNode) ASSERT e.global_id IS UNIQUE;
CREATE CONSTRAINT ON (t:Tenant) ASSERT t.id IS UNIQUE;

// Example Data Ingestion Query (called by telemetry pipeline)
MERGE (t:Tenant {id: "tenant-789", tier: "enterprise"})
MERGE (p:Prompt {hash: "a1b2c3d4", category: "legal_contract", length: 4500})
MERGE (t)-[:SUBMITTED]->(p)

MERGE (e1:ExpertNode {global_id: "exp_legal_01", specialized_in: "Contracts"})
MERGE (e2:ExpertNode {global_id: "exp_finance_04", specialized_in: "Tax"})

// Routing Event
MERGE (p)-[r1:ROUTED_TO {weight: 0.88, tokens: 4000}]->(e1)
MERGE (p)-[r2:ROUTED_TO {weight: 0.12, tokens: 500}]->(e2)

// Analytical Query: Find the most overloaded experts used by Enterprise tenants
MATCH (t:Tenant {tier: "enterprise"})-[:SUBMITTED]->(p:Prompt)-[r:ROUTED_TO]->(e:ExpertNode)
WITH e, sum(r.tokens) as total_enterprise_tokens
ORDER BY total_enterprise_tokens DESC
LIMIT 5
RETURN e.global_id, e.specialized_in, total_enterprise_tokens

// Analytical Query: Discover "Routing Bleed" (Prompts categorised as legal going to math experts)
MATCH (p:Prompt {category: "legal_contract"})-[r:ROUTED_TO]->(e:ExpertNode {specialized_in: "Math"})
WHERE r.weight > 0.05
RETURN p.hash, e.global_id, r.weight
