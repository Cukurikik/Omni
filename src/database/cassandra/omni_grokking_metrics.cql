-- OMNI Framework Cassandra Schema for Grokking Training Metrics
-- Optimized for high-throughput time-series writes during deep learning

CREATE KEYSPACE IF NOT EXISTS omni_ai
WITH replication = {'class': 'NetworkTopologyStrategy', 'datacenter1': 3};

USE omni_ai;

CREATE TABLE IF NOT EXISTS grokking_training_metrics (
    experiment_id uuid,
    epoch int,
    step int,
    train_loss float,
    val_loss float,
    train_acc float,
    val_acc float,
    weight_norm float,
    recorded_at timestamp,
    PRIMARY KEY ((experiment_id), epoch, step)
) WITH CLUSTERING ORDER BY (epoch ASC, step ASC);
