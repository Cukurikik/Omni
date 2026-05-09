// Neo4j Cypher for OMNI AI Knowledge Graph Mapping
// Associates Code Snippets to known Design Patterns

MERGE (p:Pattern {name: 'Monadic Error Handling'})
MERGE (l:Language {name: 'Rust'})
MERGE (c:CodeSnippet {id: 'omni_rust_err_01', content: 'Result<T, E>'})

MERGE (c)-[:IMPLEMENTS]->(p)
MERGE (c)-[:WRITTEN_IN]->(l)

WITH p
MATCH (otherCode)-[:IMPLEMENTS]->(p)
WHERE otherCode.id <> 'omni_rust_err_01'
RETURN otherCode.id AS similar_implementations
