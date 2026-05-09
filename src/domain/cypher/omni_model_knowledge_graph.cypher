// OMNI Database Layer — Cypher Graph Queries for Model Knowledge Graph
// Neo4j queries for model lineage, dependencies, and performance tracking.

// Create model node
CREATE (m:Model {
  id: randomUUID(),
  name: $name,
  version: $version,
  architecture: $architecture,
  parameters: $parameters,
  status: 'ready',
  createdAt: datetime()
})
RETURN m;

// Create training lineage (model trained from dataset)
MATCH (m:Model {id: $modelId})
MATCH (d:Dataset {id: $datasetId})
CREATE (m)-[:TRAINED_ON {
  epochs: $epochs,
  batchSize: $batchSize,
  learningRate: $lr,
  finalLoss: $loss,
  trainedAt: datetime()
}]->(d)
RETURN m, d;

// Create model dependency graph
MATCH (child:Model {id: $childId})
MATCH (parent:Model {id: $parentId})
CREATE (child)-[:DERIVED_FROM {
  method: $method,
  description: $description,
  createdAt: datetime()
}]->(parent)
RETURN child, parent;

// Query: Find all models derived from a base model (recursive lineage)
MATCH path = (m:Model)-[:DERIVED_FROM*1..10]->(base:Model {name: $baseName})
RETURN m.name AS model_name,
       m.version AS version,
       m.architecture AS architecture,
       length(path) AS derivation_depth
ORDER BY derivation_depth;

// Query: Find best performing models by metric
MATCH (m:Model)-[:HAS_METRIC]->(metric:Metric)
WHERE metric.name = $metricName
  AND m.status = 'deployed'
RETURN m.name, m.version, metric.value
ORDER BY metric.value DESC
LIMIT 10;

// Query: Model deployment topology
MATCH (m:Model)-[:DEPLOYED_ON]->(d:Deployment)-[:RUNS_IN]->(env:Environment)
WHERE m.id = $modelId
RETURN m.name, d.replicas, d.status, env.name AS environment, env.region
ORDER BY env.name;

// Query: Dataset usage across models
MATCH (m:Model)-[t:TRAINED_ON]->(d:Dataset)
RETURN d.name AS dataset,
       count(m) AS models_trained,
       avg(t.finalLoss) AS avg_final_loss,
       collect(m.name) AS model_names
ORDER BY models_trained DESC;

// Query: Inference performance comparison
MATCH (m:Model)-[:HAS_METRICS]->(perf:PerformanceMetrics)
WHERE m.architecture = $architecture
RETURN m.name,
       m.parameters,
       perf.latencyP50Ms,
       perf.latencyP99Ms,
       perf.throughputTokensPerSec,
       perf.memoryUsageMb
ORDER BY perf.throughputTokensPerSec DESC;

// Create experiment tracking relationship
MATCH (m:Model {id: $modelId})
CREATE (e:Experiment {
  id: randomUUID(),
  name: $experimentName,
  status: 'running',
  config: $config,
  startedAt: datetime()
})
CREATE (m)-[:HAS_EXPERIMENT]->(e)
RETURN e;

// Update experiment with results
MATCH (e:Experiment {id: $experimentId})
SET e.status = 'completed',
    e.completedAt = datetime(),
    e.results = $results
RETURN e;
