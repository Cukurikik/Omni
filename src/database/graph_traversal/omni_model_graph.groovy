// @omni-layer Database | @omni-lang Gremlin (Apache TinkerPop) | @omni-batch 17
// @omni-description Graph traversal queries: Gremlin traversals for AI model
// dependency graph, concept navigation, and impact analysis.

// === Schema Setup ===
// Create vertex labels and properties
schema.vertexLabel('Model').ifNotExists().partitionBy('model_id', Text).property('name', Text).property('architecture', Text).property('parameters', Bigint).property('version', Text).property('status', Text).create()
schema.vertexLabel('Concept').ifNotExists().partitionBy('concept_id', Text).property('name', Text).property('type', Text).property('confidence', Double).create()
schema.vertexLabel('Dataset').ifNotExists().partitionBy('dataset_id', Text).property('name', Text).property('size', Bigint).property('format', Text).create()

// Create edge labels
schema.edgeLabel('DEPENDS_ON').ifNotExists().from('Model').to('Model').property('dependency_type', Text).create()
schema.edgeLabel('TRAINED_ON').ifNotExists().from('Model').to('Dataset').property('epochs', Int).create()
schema.edgeLabel('PRODUCES').ifNotExists().from('Model').to('Concept').property('confidence', Double).create()
schema.edgeLabel('IS_A').ifNotExists().from('Concept').to('Concept').create()

// === Traversal Queries ===

// 1. Find all dependencies of a model (transitive)
g.V().has('Model', 'model_id', modelId).
  repeat(out('DEPENDS_ON')).
    until(outE('DEPENDS_ON').count().is(0)).
    emit().
  path().
    by('name').
  dedup()

// 2. Impact analysis: which models are affected if a model changes
g.V().has('Model', 'model_id', modelId).
  repeat(__.in('DEPENDS_ON')).
    until(inE('DEPENDS_ON').count().is(0)).
    emit().
  dedup().
  project('model', 'depth').
    by('name').
    by(path().count(local))

// 3. Concept taxonomy traversal
g.V().has('Concept', 'name', conceptName).
  repeat(out('IS_A')).
    until(outE('IS_A').count().is(0)).
    emit().
  path().
    by('name')

// 4. Find models that produce a specific concept
g.V().has('Concept', 'name', conceptName).
  in('PRODUCES').
  hasLabel('Model').
  project('model', 'architecture', 'confidence').
    by('name').
    by('architecture').
    by(inE('PRODUCES').values('confidence'))

// 5. Most connected models (hub analysis)
g.V().hasLabel('Model').
  project('model', 'in_deps', 'out_deps', 'datasets', 'concepts').
    by('name').
    by(__.in('DEPENDS_ON').count()).
    by(out('DEPENDS_ON').count()).
    by(out('TRAINED_ON').count()).
    by(out('PRODUCES').count()).
  order().
    by(select('in_deps'), desc).
  limit(10)

// 6. Shortest path between two models
g.V().has('Model', 'model_id', modelA).
  repeat(both('DEPENDS_ON').simplePath()).
    until(has('model_id', modelB)).
  path().
    by('name').
  limit(1)

// 7. Concept co-occurrence analysis
g.V().has('Concept', 'type', 'entity').
  as('c1').
  in('PRODUCES').
  out('PRODUCES').
  where(neq('c1')).
  as('c2').
  select('c1', 'c2').
    by('name').
  groupCount().
  order(local).
    by(values, desc).
  limit(local, 20)
