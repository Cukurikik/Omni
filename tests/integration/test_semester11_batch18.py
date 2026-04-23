import pytest
from src.compute.python_core.omni_apache_kafka_stream_engine import OmniApacheKafkaStreamEngine
from src.compute.python_core.omni_graphql_apollo_federation_engine import OmniGraphqlApolloFederationEngine
from src.compute.python_core.omni_kubeflow_ml_pipeline_engine import OmniKubeflowMlPipelineEngine
from src.compute.python_core.omni_redis_pub_sub_broker_engine import OmniRedisPubSubBrokerEngine
from src.compute.python_core.omni_rabbitmq_message_queue_engine import OmniRabbitmqMessageQueueEngine
from src.compute.python_core.omni_tensorflow_lite_edge_engine import OmniTensorflowLiteEdgeEngine
from src.compute.python_core.omni_pytorch_ddp_engine import OmniPytorchDdpEngine
from src.compute.python_core.omni_ansible_playbook_execution_engine import OmniAnsiblePlaybookExecutionEngine
from src.compute.python_core.omni_terraform_state_management_engine import OmniTerraformStateManagementEngine
from src.compute.python_core.omni_prometheus_tsdb_metric_engine import OmniPrometheusTsdbMetricEngine

# 1. OmniApacheKafkaStreamEngine
def test_kafka_valid_partitioning():
    engine = OmniApacheKafkaStreamEngine()
    result = engine.compute_kafka_partition_topological_matrix(["t1", "t2"], ["c1", "c2"])
    assert result.is_ok()
    assert result.unwrap()["total_partitions_assigned"] == 20
    assert result.unwrap()["idle_consumers_count"] == 0

def test_kafka_idle_consumers():
    engine = OmniApacheKafkaStreamEngine()
    result = engine.compute_kafka_partition_topological_matrix(["t1"], ["c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "c10", "c11"])
    assert result.is_ok()
    assert result.unwrap()["idle_consumers_count"] == 1 # 10 partitions, 11 consumers

def test_kafka_empty_input():
    engine = OmniApacheKafkaStreamEngine()
    assert not engine.compute_kafka_partition_topological_matrix([], ["c1"]).is_ok()

def test_kafka_capacity():
    engine = OmniApacheKafkaStreamEngine(1)
    assert not engine.compute_kafka_partition_topological_matrix(["t1", "t2"], ["c1", "c2"]).is_ok()

def test_kafka_diagnostics():
    engine = OmniApacheKafkaStreamEngine()
    assert "Geometry Topology" in engine.diagnostics()["complexity"]

# 2. OmniGraphqlApolloFederationEngine
def test_apollo_valid_federation():
    engine = OmniGraphqlApolloFederationEngine()
    sg = [{"name": "s1", "resolves": ["id"]}, {"name": "s2", "resolves": ["name"]}]
    ast = {"requested_fields": ["id", "name"]}
    result = engine.resolve_federated_subgraph_topology(sg, ast)
    assert result.is_ok()
    assert result.unwrap()["is_query_executable"] is True

def test_apollo_unresolved_field():
    engine = OmniGraphqlApolloFederationEngine()
    sg = [{"name": "s1", "resolves": ["id"]}]
    ast = {"requested_fields": ["id", "name"]}
    result = engine.resolve_federated_subgraph_topology(sg, ast)
    assert result.is_ok()
    assert result.unwrap()["query_fields_unresolved"] == 1

def test_apollo_invalid_inputs():
    engine = OmniGraphqlApolloFederationEngine()
    assert not engine.resolve_federated_subgraph_topology([], {}).is_ok()

def test_apollo_capacity():
    engine = OmniGraphqlApolloFederationEngine(1)
    sg = [{"resolves": ["1", "2"]}]
    ast = {"requested_fields": ["1", "2"]}
    assert not engine.resolve_federated_subgraph_topology(sg, ast).is_ok()

def test_apollo_diagnostics():
    engine = OmniGraphqlApolloFederationEngine()
    assert engine.diagnostics()["status"] == "operational"

# 3. OmniKubeflowMlPipelineEngine
def test_kubeflow_dag_valid():
    engine = OmniKubeflowMlPipelineEngine()
    nodes = [{"id": "n1"}, {"id": "n2"}]
    deps = [("n1", "n2")]
    result = engine.validate_ml_pipeline_dag_execution(nodes, deps)
    assert result.is_ok()
    assert result.unwrap()["is_valid_dag_acyclic"] is True
    assert result.unwrap()["execution_topology_order"] == ["n1", "n2"]

def test_kubeflow_dag_cycle():
    engine = OmniKubeflowMlPipelineEngine()
    nodes = [{"id": "n1"}, {"id": "n2"}]
    deps = [("n1", "n2"), ("n2", "n1")]
    result = engine.validate_ml_pipeline_dag_execution(nodes, deps)
    assert result.is_ok()
    assert result.unwrap()["is_valid_dag_acyclic"] is False

def test_kubeflow_invalid_deps():
    engine = OmniKubeflowMlPipelineEngine()
    assert not engine.validate_ml_pipeline_dag_execution([{"id": "n1"}], [("bad", "bad")]).is_ok()

def test_kubeflow_capacity():
    engine = OmniKubeflowMlPipelineEngine(1)
    assert not engine.validate_ml_pipeline_dag_execution([{"id":"1"}, {"id":"2"}], []).is_ok()

def test_kubeflow_diagnostics():
    engine = OmniKubeflowMlPipelineEngine()
    assert "Cycle Detection" in engine.diagnostics()["complexity"]

# 4. OmniRedisPubSubBrokerEngine
def test_redis_pubsub_broadcast():
    engine = OmniRedisPubSubBrokerEngine()
    ch = ["test.1"]
    sub = [{"sub_id": "s1", "patterns": ["test.*"]}]
    msg = [{"channel": "test.1", "payload": "p1"}]
    result = engine.calculate_pubsub_broadcast_matrix(ch, sub, msg)
    assert result.is_ok()
    assert result.unwrap()["total_messages_delivered"] == 1

def test_redis_pubsub_no_match():
    engine = OmniRedisPubSubBrokerEngine()
    ch = ["test.1"]
    sub = [{"sub_id": "s1", "patterns": ["other.*"]}]
    msg = [{"channel": "test.1", "payload": "p1"}]
    result = engine.calculate_pubsub_broadcast_matrix(ch, sub, msg)
    assert result.is_ok()
    assert result.unwrap()["total_messages_delivered"] == 0

def test_redis_pubsub_invalid_inputs():
    engine = OmniRedisPubSubBrokerEngine()
    assert not engine.calculate_pubsub_broadcast_matrix([], [], []).is_ok()

def test_redis_pubsub_capacity():
    engine = OmniRedisPubSubBrokerEngine(1)
    assert not engine.calculate_pubsub_broadcast_matrix(["a", "b"], [{"sub_id": "1"}], [{"channel":"a"}]).is_ok()

def test_redis_pubsub_diagnostics():
    engine = OmniRedisPubSubBrokerEngine()
    assert engine.diagnostics()["status"] == "operational"

# 5. OmniRabbitmqMessageQueueEngine
def test_rabbitmq_direct_routing():
    engine = OmniRabbitmqMessageQueueEngine()
    ex = [{"name": "e1", "type": "direct"}]
    b = [{"queue": "q1", "exchange": "e1", "routing_key": "k1"}]
    msg = [{"exchange": "e1", "routing_key": "k1"}]
    result = engine.execute_amqp_exchange_routing_topology(ex, b, msg)
    assert result.is_ok()
    assert result.unwrap()["unroutable_messages_dropped"] == 0
    assert result.unwrap()["queue_delivery_matrix"]["q1"] == 1

def test_rabbitmq_fanout_routing():
    engine = OmniRabbitmqMessageQueueEngine()
    ex = [{"name": "e1", "type": "fanout"}]
    b = [{"queue": "q1", "exchange": "e1"}]
    msg = [{"exchange": "e1", "routing_key": "any"}]
    result = engine.execute_amqp_exchange_routing_topology(ex, b, msg)
    assert result.is_ok()
    assert result.unwrap()["queue_delivery_matrix"]["q1"] == 1

def test_rabbitmq_empty():
    engine = OmniRabbitmqMessageQueueEngine()
    assert not engine.execute_amqp_exchange_routing_topology([], [], []).is_ok()

def test_rabbitmq_capacity():
    engine = OmniRabbitmqMessageQueueEngine(1)
    ex = [{"name": "e"}]
    b = [{"queue": "q", "exchange": "e"}]
    msg = [{"exchange": "e"}, {"exchange": "e"}]
    assert not engine.execute_amqp_exchange_routing_topology(ex, b, msg).is_ok()

def test_rabbitmq_diagnostics():
    engine = OmniRabbitmqMessageQueueEngine()
    assert "AMQP Exchange" in engine.diagnostics()["complexity"]

# 6. OmniTensorflowLiteEdgeEngine
def test_tflite_edge_memory():
    engine = OmniTensorflowLiteEdgeEngine()
    tensors = [{"id": "t1", "dtype": "float32", "shape": [1, 10]}]
    result = engine.compute_edge_tensor_memory_topology(tensors)
    assert result.is_ok()
    assert result.unwrap()["total_tensor_memory_bytes"] == 40

def test_tflite_edge_invalid_dtype():
    engine = OmniTensorflowLiteEdgeEngine()
    assert not engine.compute_edge_tensor_memory_topology([{"id": "t1", "dtype": "bad"}]).is_ok()

def test_tflite_edge_empty():
    engine = OmniTensorflowLiteEdgeEngine()
    assert not engine.compute_edge_tensor_memory_topology([]).is_ok()

def test_tflite_edge_capacity():
    engine = OmniTensorflowLiteEdgeEngine(1)
    t = [{"id": "1", "dtype": "float32", "shape": [1, 1024, 1024, 10]}]
    assert not engine.compute_edge_tensor_memory_topology(t).is_ok()

def test_tflite_edge_diagnostics():
    engine = OmniTensorflowLiteEdgeEngine()
    assert "TFLite Edge" in engine.diagnostics()["complexity"]

# 7. OmniPytorchDdpEngine
def test_ddp_sync_valid():
    engine = OmniPytorchDdpEngine()
    result = engine.validate_distributed_gradient_sync_topology([0, 1], [100.0, 100.0])
    assert result.is_ok()
    assert result.unwrap()["is_cluster_synchronized"] is True

def test_ddp_sync_variance():
    engine = OmniPytorchDdpEngine()
    result = engine.validate_distributed_gradient_sync_topology([0, 1], [10.0, 100.0])
    assert result.is_ok()
    assert result.unwrap()["is_cluster_synchronized"] is False

def test_ddp_sync_invalid():
    engine = OmniPytorchDdpEngine()
    assert not engine.validate_distributed_gradient_sync_topology([0], []).is_ok()

def test_ddp_sync_capacity():
    engine = OmniPytorchDdpEngine(1)
    assert not engine.validate_distributed_gradient_sync_topology([0, 1], [10.0, 10.0]).is_ok()

def test_ddp_sync_diagnostics():
    engine = OmniPytorchDdpEngine()
    assert "Distributed Data Parallel" in engine.diagnostics()["complexity"]

# 8. OmniAnsiblePlaybookExecutionEngine
def test_ansible_convergence():
    engine = OmniAnsiblePlaybookExecutionEngine()
    h = ["h1"]
    t = [{"module": "apt"}]
    result = engine.execute_playbook_convergence_matrix(h, t)
    assert result.is_ok()
    assert result.unwrap()["convergence_matrix"]["h1"]["changed"] == 1

def test_ansible_ok_convergence():
    engine = OmniAnsiblePlaybookExecutionEngine()
    h = ["h1"]
    t = [{"module": "service"}]
    result = engine.execute_playbook_convergence_matrix(h, t)
    assert result.is_ok()
    assert result.unwrap()["convergence_matrix"]["h1"]["ok"] == 1

def test_ansible_invalid_module():
    engine = OmniAnsiblePlaybookExecutionEngine()
    assert not engine.execute_playbook_convergence_matrix(["h1"], [{}]).is_ok()

def test_ansible_capacity():
    engine = OmniAnsiblePlaybookExecutionEngine(1)
    assert not engine.execute_playbook_convergence_matrix(["h"], [{"module": "a"}, {"module": "b"}]).is_ok()

def test_ansible_diagnostics():
    engine = OmniAnsiblePlaybookExecutionEngine()
    assert engine.diagnostics()["status"] == "operational"

# 9. OmniTerraformStateManagementEngine
def test_terraform_valid_dag():
    engine = OmniTerraformStateManagementEngine()
    res = [{"module": "r1"}, {"module": "r2", "depends_on": ["r1"]}]
    result = engine.evaluate_tfstate_dependency_dag(res)
    assert result.is_ok()
    assert result.unwrap()["is_dag_acyclic_valid"] is True

def test_terraform_invalid_deps():
    engine = OmniTerraformStateManagementEngine()
    res = [{"module": "r1"}] # missing depends_on is handled gracefully
    result = engine.evaluate_tfstate_dependency_dag(res)
    assert result.is_ok()
    assert result.unwrap()["independent_root_resources"] == 1

def test_terraform_missing_module():
    engine = OmniTerraformStateManagementEngine()
    assert not engine.evaluate_tfstate_dependency_dag([{"no_module": 1}]).is_ok()

def test_terraform_capacity():
    engine = OmniTerraformStateManagementEngine(1)
    assert not engine.evaluate_tfstate_dependency_dag([{"module": "1"}, {"module": "2"}]).is_ok()

def test_terraform_diagnostics():
    engine = OmniTerraformStateManagementEngine()
    assert "Infrastructure As Code" in engine.diagnostics()["complexity"]

# 10. OmniPrometheusTsdbMetricEngine
def test_promql_valid_window():
    engine = OmniPrometheusTsdbMetricEngine()
    result = engine.execute_promql_temporal_aggregation([10, 20, 30], [2.0, 4.0, 6.0], 15)
    assert result.is_ok()
    assert result.unwrap()["last_aggregated_value"] == 5.0 # (4 + 6) / 2

def test_promql_invalid_lengths():
    engine = OmniPrometheusTsdbMetricEngine()
    assert not engine.execute_promql_temporal_aggregation([10], [1, 2], 10).is_ok()

def test_promql_zero_window():
    engine = OmniPrometheusTsdbMetricEngine()
    assert not engine.execute_promql_temporal_aggregation([10], [1], 0).is_ok()

def test_promql_capacity():
    engine = OmniPrometheusTsdbMetricEngine(2)
    assert not engine.execute_promql_temporal_aggregation([1, 2, 3], [1, 2, 3], 10).is_ok()

def test_promql_diagnostics():
    engine = OmniPrometheusTsdbMetricEngine()
    assert engine.diagnostics()["status"] == "operational"
