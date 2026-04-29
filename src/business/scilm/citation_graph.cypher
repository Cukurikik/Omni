// OmniResult handled implicitly by Neo4j driver wrappers
// Cypher query for Awesome-Scientific-Language-Models citation graph

MATCH (p1:Paper)-[r:CITES]->(p2:Paper)
WHERE p1.domain = "LLM" AND p2.domain = "Biology"
WITH p1, p2, r
ORDER BY r.weight DESC
LIMIT 100
RETURN {
    value: collect({source: p1.title, target: p2.title}),
    error: null,
    is_ok: true
} AS OmniResult
