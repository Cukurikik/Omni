// OMNI Framework - Gremlin Query for Warren Buffet NLP Entities
// Traverses the knowledge graph to find connections between extracted financial entities

// Find all documents where "Berkshire Hathaway" is mentioned
g.V().hasLabel('Entity').has('name', 'Berkshire Hathaway')
 .inE('MENTIONS').outV().hasLabel('Document')
 .as('doc')
 // Find other entities mentioned in the same document
 .outE('MENTIONS').inV().hasLabel('Entity')
 .where(neq('Berkshire Hathaway'))
 // Group and count co-occurrences
 .groupCount().by('name')
 .order(local).by(values, desc)
 .limit(local, 10)
