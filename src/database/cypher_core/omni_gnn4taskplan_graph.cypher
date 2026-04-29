// Omni GNN4TaskPlan Graph (Cypher)
// Database Layer: Task planning graph with GNN node embeddings.
// Ref: WxxShirley/GNN4TaskPlan — NeurIPS 2024
CREATE CONSTRAINT task_unique IF NOT EXISTS FOR (t:Task) REQUIRE t.task_id IS UNIQUE;
MERGE (t1:Task {task_id: $task_id, description: $desc})
SET t1.embedding = $embedding, t1.priority = $priority
WITH t1
UNWIND $deps AS dep_id
MATCH (t2:Task {task_id: dep_id})
MERGE (t1)-[:DEPENDS_ON]->(t2)
RETURN t1.task_id;
