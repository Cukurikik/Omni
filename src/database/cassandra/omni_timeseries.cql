-- OMNI Cassandra CQL for High-Throughput Time-Series Sensor Data
CREATE KEYSPACE IF NOT EXISTS omni_telemetry 
WITH replication = {'class': 'NetworkTopologyStrategy', 'datacenter1': '3'} 
AND durable_writes = true;

USE omni_telemetry;

CREATE TABLE IF NOT EXISTS gpu_metrics (
    node_id uuid,
    metric_time timestamp,
    temperature float,
    utilization float,
    memory_used float,
    PRIMARY KEY ((node_id), metric_time)
) WITH CLUSTERING ORDER BY (metric_time DESC)
  AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_unit': 'HOURS', 'compaction_window_size': 1};

-- Index for quick lookup on hot nodes
CREATE INDEX IF NOT EXISTS ON gpu_metrics (temperature);
