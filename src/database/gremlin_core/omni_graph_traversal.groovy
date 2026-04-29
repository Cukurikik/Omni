// Omni Graph Traversal Engine (Gremlin)
// Traverses relationships between microservices in the Polyglot space.

g.V().hasLabel('OmniEngine')
  .has('layer', 'Compute')
  .out('depends_on')
  .hasLabel('OmniKernel')
  .where(outE('validates').count().is(gte(1)))
  .path()
  .by('name')
  .toList()
