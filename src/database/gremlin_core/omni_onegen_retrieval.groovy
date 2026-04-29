// Omni OneGen Retrieval Traversal (Gremlin)
// Database Layer: Document retrieval graph traversal.
// Ref: zjunlp/OneGen — EMNLP 2024
g.V().hasLabel('query')
 .outE('retrieves')
 .inV().hasLabel('document')
 .order().by('score', Order.desc)
 .limit(10)
 .path().by('text').by('score')
 .toList()
