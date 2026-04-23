import pytest
from src.compute.python_core.omni_django_rest_swagger_engine import OmniDjangoRestSwaggerEngine
from src.compute.python_core.omni_svelte_kit_ssr_engine import OmniSvelteKitSsrEngine
from src.compute.python_core.omni_tensorflow_lite_mobile_engine import OmniTensorflowLiteMobileEngine
from src.compute.python_core.omni_kafka_consumer_group_engine import OmniKafkaConsumerGroupEngine
from src.compute.python_core.omni_unity3d_scene_graph_engine import OmniUnity3dSceneGraphEngine
from src.compute.python_core.omni_nestjs_microservices_engine import OmniNestjsMicroservicesEngine
from src.compute.python_core.omni_spring_boot_hibernate_engine import OmniSpringBootHibernateEngine
from src.compute.python_core.omni_celery_task_broker_engine import OmniCeleryTaskBrokerEngine
from src.compute.python_core.omni_solidity_smart_contract_engine import OmniSoliditySmartContractEngine
from src.compute.python_core.omni_go_grpc_protobuf_engine import OmniGoGrpcProtobufEngine

# ---------------------------------------------------------
# ENGINE 1: OmniDjangoRestSwaggerEngine
# ---------------------------------------------------------
def test_django_rest_swagger_diagnostics():
    en = OmniDjangoRestSwaggerEngine()
    assert en.diagnostics()["status"] == "operational"

def test_django_rest_swagger_valid():
    en = OmniDjangoRestSwaggerEngine(25)
    endpoints = [{"path": "/api/v1", "method": "GET"}, {"path": "/api/users", "method": "POST"}]
    res = en.execute_api_docs_math_matrix(endpoints)
    assert res.is_ok()
    out = res.unwrap()
    assert out["endpoints_documented"] == 2
    assert out["http_methods_distribution"]["GET"] == 1
    assert "/api/users" in out["verified_paths_matrix"]

def test_django_rest_swagger_exceeded():
    en = OmniDjangoRestSwaggerEngine(1)
    endpoints = [{"path": "/api/v1", "method": "GET"}, {"path": "/api/users", "method": "POST"}]
    assert not en.execute_api_docs_math_matrix(endpoints).is_ok()

def test_django_rest_swagger_invalid_path():
    en = OmniDjangoRestSwaggerEngine()
    endpoints = [{"path": "api/v1", "method": "GET"}] # Missing leading slash
    assert not en.execute_api_docs_math_matrix(endpoints).is_ok()

def test_django_rest_swagger_empty():
    en = OmniDjangoRestSwaggerEngine()
    assert not en.execute_api_docs_math_matrix([]).is_ok()

# ---------------------------------------------------------
# ENGINE 2: OmniSvelteKitSsrEngine
# ---------------------------------------------------------
def test_svelte_ssr_diagnostics():
    en = OmniSvelteKitSsrEngine()
    assert en.diagnostics()["status"] == "operational"

def test_svelte_ssr_valid():
    en = OmniSvelteKitSsrEngine(10.0)
    # Node 1: 0.5 + 0.5 = 1.0. Node 2: 0.5. Total: 1.5ms
    nodes = [{"tag": "div", "children_count": 5}, {"tag": "h1", "children_count": 0}]
    res = en.execute_dom_hydration_metric(nodes)
    assert res.is_ok()
    out = res.unwrap()
    assert out["simulated_ssr_latency_ms"] == 1.5
    assert out["ssr_latency_acceptable"] is True

def test_svelte_ssr_exceeded():
    en = OmniSvelteKitSsrEngine(1.0) # 1ms limit
    nodes = [{"tag": "div", "children_count": 50}] # 0.5 + 5.0 = 5.5ms
    res = en.execute_dom_hydration_metric(nodes)
    assert res.unwrap()["ssr_latency_acceptable"] is False

def test_svelte_ssr_negative_children():
    en = OmniSvelteKitSsrEngine()
    assert not en.execute_dom_hydration_metric([{"tag": "div", "children_count": -5}]).is_ok()

def test_svelte_ssr_empty():
    en = OmniSvelteKitSsrEngine()
    assert not en.execute_dom_hydration_metric([]).is_ok()

# ---------------------------------------------------------
# ENGINE 3: OmniTensorflowLiteMobileEngine
# ---------------------------------------------------------
def test_tf_lite_diagnostics():
    en = OmniTensorflowLiteMobileEngine()
    assert en.diagnostics()["status"] == "operational"

def test_tf_lite_valid():
    en = OmniTensorflowLiteMobileEngine(10.0)
    layers = [{"neurons": 1024, "connections": 1024}] # ~ 1 MB
    res = en.compute_mobile_tensor_weights(layers)
    assert res.is_ok()
    out = res.unwrap()
    assert out["total_quantized_parameters"] == 1048576
    assert out["is_mobile_compliant"] is True

def test_tf_lite_exceeded():
    en = OmniTensorflowLiteMobileEngine(1.0)
    layers = [{"neurons": 2048, "connections": 2048}] # ~ 4 MB
    res = en.compute_mobile_tensor_weights(layers)
    assert res.unwrap()["is_mobile_compliant"] is False

def test_tf_lite_negative_metrics():
    en = OmniTensorflowLiteMobileEngine()
    assert not en.compute_mobile_tensor_weights([{"neurons": -10, "connections": 10}]).is_ok()

def test_tf_lite_empty():
    en = OmniTensorflowLiteMobileEngine()
    assert not en.compute_mobile_tensor_weights([]).is_ok()

# ---------------------------------------------------------
# ENGINE 4: OmniKafkaConsumerGroupEngine
# ---------------------------------------------------------
def test_kafka_consumer_diagnostics():
    en = OmniKafkaConsumerGroupEngine()
    assert en.diagnostics()["status"] == "operational"

def test_kafka_consumer_valid_balanced():
    en = OmniKafkaConsumerGroupEngine(3)
    consumers = ["C1", "C2"]
    # 3 partitions, 2 consumers -> C1 gets 2, C2 gets 1
    res = en.calculate_topic_partition_assignment(consumers)
    assert res.is_ok()
    out = res.unwrap()
    assert len(out["fully_balanced_distribution_matrix"]["C1"]) == 2
    assert len(out["fully_balanced_distribution_matrix"]["C2"]) == 1

def test_kafka_consumer_starved():
    en = OmniKafkaConsumerGroupEngine(2)
    consumers = ["C1", "C2", "C3"]
    # 2 partitions, 3 consumers -> C3 is starved
    res = en.calculate_topic_partition_assignment(consumers)
    assert res.is_ok()
    assert "C3" in res.unwrap()["idle_starved_consumers"]

def test_kafka_consumer_no_partitions():
    en = OmniKafkaConsumerGroupEngine(0)
    assert not en.calculate_topic_partition_assignment(["C1"]).is_ok()

def test_kafka_consumer_empty():
    en = OmniKafkaConsumerGroupEngine()
    assert not en.calculate_topic_partition_assignment([]).is_ok()

# ---------------------------------------------------------
# ENGINE 5: OmniUnity3dSceneGraphEngine
# ---------------------------------------------------------
def test_unity3d_graph_diagnostics():
    en = OmniUnity3dSceneGraphEngine()
    assert en.diagnostics()["status"] == "operational"

def test_unity3d_graph_valid():
    en = OmniUnity3dSceneGraphEngine(10)
    graph = {"id": "root", "children": [{"id": "target", "children": []}]}
    res = en.evaluate_mathematical_transform_matrix(graph, "target")
    assert res.is_ok()
    out = res.unwrap()
    assert out["node_was_located"] is True
    assert out["found_at_depth_geometry"] == 1

def test_unity3d_graph_not_found():
    en = OmniUnity3dSceneGraphEngine(10)
    graph = {"id": "root", "children": []}
    res = en.evaluate_mathematical_transform_matrix(graph, "target")
    assert res.unwrap()["node_was_located"] is False

def test_unity3d_graph_depth_recursion_limit():
    en = OmniUnity3dSceneGraphEngine(1)
    graph = {"id": "r", "children": [{"id": "c1", "children": [{"id": "c2", "children": []}]}]}
    assert not en.evaluate_mathematical_transform_matrix(graph, "c2").is_ok()

def test_unity3d_graph_empty():
    en = OmniUnity3dSceneGraphEngine()
    assert not en.evaluate_mathematical_transform_matrix({}, "t").is_ok()

# ---------------------------------------------------------
# ENGINE 6: OmniNestjsMicroservicesEngine
# ---------------------------------------------------------
def test_nestjs_microservices_diagnostics():
    en = OmniNestjsMicroservicesEngine()
    assert en.diagnostics()["status"] == "operational"

def test_nestjs_microservices_valid():
    en = OmniNestjsMicroservicesEngine(1000)
    msgs = [{"pattern": "auth", "payload_bytes": 500}, {"pattern": "db", "payload_bytes": 100}]
    res = en.map_message_pattern_broker(msgs)
    assert res.is_ok()
    out = res.unwrap()
    assert out["total_valid_bytes_processed"] == 600
    assert "auth" in out["successfully_routed_patterns"]

def test_nestjs_microservices_dropped():
    en = OmniNestjsMicroservicesEngine(500)
    msgs = [{"pattern": "large", "payload_bytes": 1000}]
    res = en.map_message_pattern_broker(msgs)
    assert "large" in res.unwrap()["dropped_payload_limit_violations"]

def test_nestjs_microservices_negative_bytes():
    en = OmniNestjsMicroservicesEngine()
    assert not en.map_message_pattern_broker([{"pattern": "p", "payload_bytes": -10}]).is_ok()

def test_nestjs_microservices_empty():
    en = OmniNestjsMicroservicesEngine()
    assert not en.map_message_pattern_broker([]).is_ok()

# ---------------------------------------------------------
# ENGINE 7: OmniSpringBootHibernateEngine
# ---------------------------------------------------------
def test_spring_hibernate_diagnostics():
    en = OmniSpringBootHibernateEngine()
    assert en.diagnostics()["status"] == "operational"

def test_spring_hibernate_valid():
    en = OmniSpringBootHibernateEngine(10)
    ent = [{"table": "user", "relations": ["profile"]}, {"table": "profile", "relations": []}]
    res = en.execute_relational_schema_validation(ent)
    assert res.is_ok()
    out = res.unwrap()
    assert out["is_schema_integrity_valid"] is True
    assert out["total_valid_relationships"] == 1

def test_spring_hibernate_orphan_relation():
    en = OmniSpringBootHibernateEngine(10)
    ent = [{"table": "user", "relations": ["profile"]}] # Profile not defined
    res = en.execute_relational_schema_validation(ent)
    assert res.unwrap()["is_schema_integrity_valid"] is False
    assert "profile" in res.unwrap()["orphan_schema_references"]

def test_spring_hibernate_exceeded_tables():
    en = OmniSpringBootHibernateEngine(1)
    ent = [{"table": "t1"}, {"table": "t2"}]
    assert not en.execute_relational_schema_validation(ent).is_ok()

def test_spring_hibernate_empty():
    en = OmniSpringBootHibernateEngine()
    assert not en.execute_relational_schema_validation([]).is_ok()

# ---------------------------------------------------------
# ENGINE 8: OmniCeleryTaskBrokerEngine
# ---------------------------------------------------------
def test_celery_broker_diagnostics():
    en = OmniCeleryTaskBrokerEngine()
    assert en.diagnostics()["status"] == "operational"

def test_celery_broker_valid_sort():
    en = OmniCeleryTaskBrokerEngine(10)
    tasks = [{"id": 1, "priority": 1}, {"id": 2, "priority": 9}]
    # Active workers = 1, should schedule id 2 (high priority), leave id 1 in backlog
    res = en.execute_task_queue_routing(tasks, 1)
    assert res.is_ok()
    out = res.unwrap()
    assert out["tasks_assigned"] == 1
    assert out["tasks_in_backlog"] == 1

def test_celery_broker_capacity_exceed():
    en = OmniCeleryTaskBrokerEngine(1)
    tasks = [{"id": 1, "priority": 1}, {"id": 2, "priority": 9}]
    assert not en.execute_task_queue_routing(tasks, 5).is_ok()

def test_celery_broker_no_workers():
    en = OmniCeleryTaskBrokerEngine()
    assert not en.execute_task_queue_routing([{"id": 1, "priority": 1}], 0).is_ok()

def test_celery_broker_empty():
    en = OmniCeleryTaskBrokerEngine()
    assert not en.execute_task_queue_routing([], 2).is_ok()

# ---------------------------------------------------------
# ENGINE 9: OmniSoliditySmartContractEngine
# ---------------------------------------------------------
def test_solidity_contract_diagnostics():
    en = OmniSoliditySmartContractEngine()
    assert en.diagnostics()["status"] == "operational"

def test_solidity_contract_valid():
    en = OmniSoliditySmartContractEngine(300000)
    # ADD (3) + SSTORE (20000) = 20003
    ops = ["ADD", "SSTORE"]
    res = en.compute_gas_execution_cost(ops)
    assert res.is_ok()
    out = res.unwrap()
    assert out["total_gas_consumed"] == 20003
    assert out["is_block_compliant"] is True

def test_solidity_contract_exceeded():
    en = OmniSoliditySmartContractEngine(1000)
    ops = ["SSTORE"]
    res = en.compute_gas_execution_cost(ops)
    assert res.unwrap()["is_block_compliant"] is False

def test_solidity_contract_unmapped_op():
    en = OmniSoliditySmartContractEngine(1000)
    res = en.compute_gas_execution_cost(["UNKNOWN_OP"])
    assert "UNKNOWN_OP" in res.unwrap()["unmapped_instructions_warn"]

def test_solidity_contract_empty():
    en = OmniSoliditySmartContractEngine()
    assert not en.compute_gas_execution_cost([]).is_ok()

# ---------------------------------------------------------
# ENGINE 10: OmniGoGrpcProtobufEngine
# ---------------------------------------------------------
def test_grpc_protobuf_diagnostics():
    en = OmniGoGrpcProtobufEngine()
    assert en.diagnostics()["status"] == "operational"

def test_grpc_protobuf_valid():
    en = OmniGoGrpcProtobufEngine(1000)
    # int32 (4) * 1 + string (1) * 10 = 14 bytes
    fields = [{"type": "int32", "length": 1}, {"type": "string", "length": 10}]
    res = en.execute_protobuf_serialization_size(fields)
    assert res.is_ok()
    out = res.unwrap()
    assert out["simulated_byte_size"] == 14
    assert out["protobuf_message_valid"] is True

def test_grpc_protobuf_exceeded():
    en = OmniGoGrpcProtobufEngine(10)
    fields = [{"type": "string", "length": 50}]
    res = en.execute_protobuf_serialization_size(fields)
    assert res.unwrap()["protobuf_message_valid"] is False

def test_grpc_protobuf_negative_length():
    en = OmniGoGrpcProtobufEngine()
    assert not en.execute_protobuf_serialization_size([{"type": "string", "length": -5}]).is_ok()

def test_grpc_protobuf_empty():
    en = OmniGoGrpcProtobufEngine()
    assert not en.execute_protobuf_serialization_size([]).is_ok()

