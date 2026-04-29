// Omni KnowPAT Preference Graph (Cypher)
// Database Layer: Structural representation of knowledge preference alignments for QA.

// Deterministic query to establish a preferred alignment trajectory
MATCH (q:Question {domain: $target_domain})
MATCH (a:Answer {id: $answer_id})
WHERE a.confidence_score >= 0.85
MERGE (q)-[rel:PREFERRED_OVER]->(a)
ON CREATE SET rel.alignment_weight = 1.0, rel.established_at = timestamp()
ON MATCH SET rel.alignment_weight = rel.alignment_weight + 0.1
RETURN q.id, a.id, rel.alignment_weight;
