# OMNI Framework - Redis Cluster Deployment (Terraform)
# Provisions an AWS ElastiCache Redis cluster optimized for the high-throughput
# Pub/Sub requirements of MoE streaming and quota management.

resource "aws_elasticache_subnet_group" "omni_redis_subnet" {
  name       = "omni-redis-subnet-group"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}

resource "aws_elasticache_replication_group" "omni_moe_redis" {
  replication_group_id          = "omni-moe-redis-cluster"
  description                   = "OMNI Redis for MoE Token Streaming & Quotas"
  node_type                     = "cache.m6g.xlarge" # ARM-based, high network performance
  port                          = 6379
  parameter_group_name          = "default.redis7.cluster.on"
  
  automatic_failover_enabled    = true
  multi_az_enabled              = true
  
  # Clustering enabled for horizontal scaling of Pub/Sub channels
  cluster_mode {
    replicas_per_node_group = 1
    num_node_groups         = 3
  }

  subnet_group_name          = aws_elasticache_subnet_group.omni_redis_subnet.name
  security_group_ids         = [aws_security_group.redis_sg.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  tags = {
    Environment = "Production"
    System      = "OMNI-MoE"
  }
}
