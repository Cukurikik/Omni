import pytest
from src.compute.python_core.omni_laravel_eloquent_orm_engine import OmniLaravelEloquentOrmEngine
from src.compute.python_core.omni_rabbitmq_message_broker_engine import OmniRabbitmqMessageBrokerEngine
from src.compute.python_core.omni_react_hook_form_engine import OmniReactHookFormEngine
from src.compute.python_core.omni_graphql_yoga_server_engine import OmniGraphqlYogaServerEngine
from src.compute.python_core.omni_kubernetes_ingress_nginx_engine import OmniKubernetesIngressNginxEngine
from src.compute.python_core.omni_elasticsearch_lucene_query_engine import OmniElasticsearchLuceneQueryEngine
from src.compute.python_core.omni_redis_pubsub_channel_engine import OmniRedisPubsubChannelEngine
from src.compute.python_core.omni_prometheus_metrics_scraper_engine import OmniPrometheusMetricsScraperEngine
from src.compute.python_core.omni_docker_swarm_orchestrator_engine import OmniDockerSwarmOrchestratorEngine
from src.compute.python_core.omni_angular_rxjs_observable_engine import OmniAngularRxjsObservableEngine

# ---------------------------------------------------------
# ENGINE 1: OmniLaravelEloquentOrmEngine
# ---------------------------------------------------------
def test_laravel_orm_diagnostics():
    en = OmniLaravelEloquentOrmEngine()
    assert en.diagnostics()["status"] == "operational"

def test_laravel_orm_valid():
    en = OmniLaravelEloquentOrmEngine(5)
    models = [{"model": "User", "with": ["posts.comments.author"]}]
    res = en.execute_eloquent_query_mapping(models)
    assert res.is_ok()
    out = res.unwrap()
    assert out["maximum_nesting_depth_traced"] == 3
    assert "author" in out["extracted_relational_components"]

def test_laravel_orm_exceeded():
    en = OmniLaravelEloquentOrmEngine(1)
    models = [{"model": "User", "with": ["posts.comments"]}] # depth 2
    assert not en.execute_eloquent_query_mapping(models).is_ok()

def test_laravel_orm_missing_model():
    en = OmniLaravelEloquentOrmEngine()
    assert not en.execute_eloquent_query_mapping([{"with": ["posts"]}]).is_ok()

def test_laravel_orm_empty():
    en = OmniLaravelEloquentOrmEngine()
    assert not en.execute_eloquent_query_mapping([]).is_ok()

# ---------------------------------------------------------
# ENGINE 2: OmniRabbitmqMessageBrokerEngine
# ---------------------------------------------------------
def test_rabbitmq_broker_diagnostics():
    en = OmniRabbitmqMessageBrokerEngine()
    assert en.diagnostics()["status"] == "operational"

def test_rabbitmq_broker_wildcard_match():
    en = OmniRabbitmqMessageBrokerEngine(10)
    ex = [{"bindings": [{"queue": "err1", "key": "error.*"}]}]
    res = en.calculate_topic_exchange_routing(ex, "error.db")
    assert res.is_ok()
    assert "err1" in res.unwrap()["delivered_queues_vector"]

def test_rabbitmq_broker_hash_match():
    en = OmniRabbitmqMessageBrokerEngine(10)
    ex = [{"bindings": [{"queue": "err2", "key": "log.#"}]}]
    res = en.calculate_topic_exchange_routing(ex, "log.auth.fail")
    assert res.is_ok()
    assert "err2" in res.unwrap()["delivered_queues_vector"]

def test_rabbitmq_broker_no_match():
    en = OmniRabbitmqMessageBrokerEngine(10)
    ex = [{"bindings": [{"queue": "err1", "key": "error.*"}]}]
    res = en.calculate_topic_exchange_routing(ex, "info.db")
    assert res.is_ok()
    assert res.unwrap()["delivery_success"] is False

def test_rabbitmq_broker_empty():
    en = OmniRabbitmqMessageBrokerEngine()
    assert not en.calculate_topic_exchange_routing([], "k").is_ok()

# ---------------------------------------------------------
# ENGINE 3: OmniReactHookFormEngine
# ---------------------------------------------------------
def test_react_hook_form_diagnostics():
    en = OmniReactHookFormEngine()
    assert en.diagnostics()["status"] == "operational"

def test_react_hook_form_valid():
    en = OmniReactHookFormEngine(10)
    schema = {"email": {"required": True, "minLength": 5}}
    payload = {"email": "hello@world"}
    res = en.evaluate_form_validation_schema(schema, payload)
    assert res.is_ok()
    assert res.unwrap()["is_form_payload_valid"] is True

def test_react_hook_form_required_failed():
    en = OmniReactHookFormEngine(10)
    schema = {"email": {"required": True}}
    res = en.evaluate_form_validation_schema(schema, {})
    assert res.is_ok()
    assert "REQUIRED_CONSTRAINT_FAILED" in res.unwrap()["validation_errors_matrix"]["email"]

def test_react_hook_form_minlength_failed():
    en = OmniReactHookFormEngine(10)
    schema = {"email": {"minLength": 10}}
    res = en.evaluate_form_validation_schema(schema, {"email": "ab"})
    assert res.is_ok()
    assert "MIN_LENGTH_CONSTRAINT_FAILED" in res.unwrap()["validation_errors_matrix"]["email"]

def test_react_hook_form_empty():
    en = OmniReactHookFormEngine()
    assert not en.evaluate_form_validation_schema({}, {}).is_ok()

# ---------------------------------------------------------
# ENGINE 4: OmniGraphqlYogaServerEngine
# ---------------------------------------------------------
def test_graphql_yoga_diagnostics():
    en = OmniGraphqlYogaServerEngine()
    assert en.diagnostics()["status"] == "operational"

def test_graphql_yoga_valid():
    en = OmniGraphqlYogaServerEngine(100)
    ast = [{"cost": 10, "children": [{"cost": 50}]}]
    res = en.compute_ast_query_complexity(ast)
    assert res.is_ok()
    assert res.unwrap()["total_computed_complexity"] == 60
    assert res.unwrap()["is_complexity_valid"] is True

def test_graphql_yoga_exceeded():
    en = OmniGraphqlYogaServerEngine(50)
    ast = [{"cost": 10, "children": [{"cost": 50}]}] # total 60
    res = en.compute_ast_query_complexity(ast)
    assert res.unwrap()["is_complexity_valid"] is False

def test_graphql_yoga_negative_cost():
    en = OmniGraphqlYogaServerEngine()
    assert not en.compute_ast_query_complexity([{"cost": -10}]).is_ok()

def test_graphql_yoga_empty():
    en = OmniGraphqlYogaServerEngine()
    assert not en.compute_ast_query_complexity([]).is_ok()

# ---------------------------------------------------------
# ENGINE 5: OmniKubernetesIngressNginxEngine
# ---------------------------------------------------------
def test_k8s_ingress_diagnostics():
    en = OmniKubernetesIngressNginxEngine()
    assert en.diagnostics()["status"] == "operational"

def test_k8s_ingress_valid():
    en = OmniKubernetesIngressNginxEngine(10)
    rules = [{"host": "api", "paths": ["/auth"], "service": "s1"}]
    res = en.execute_host_routing_topology(rules, "api", "/auth/login")
    assert res.is_ok()
    assert res.unwrap()["target_service_routed"] == "s1"

def test_k8s_ingress_host_mismatch():
    en = OmniKubernetesIngressNginxEngine(10)
    rules = [{"host": "api", "paths": ["/auth"], "service": "s1"}]
    res = en.execute_host_routing_topology(rules, "web", "/auth/login")
    assert res.unwrap()["target_service_routed"] is None

def test_k8s_ingress_path_mismatch():
    en = OmniKubernetesIngressNginxEngine(10)
    rules = [{"host": "api", "paths": ["/auth"], "service": "s1"}]
    res = en.execute_host_routing_topology(rules, "api", "/data")
    assert res.unwrap()["target_service_routed"] is None

def test_k8s_ingress_empty():
    en = OmniKubernetesIngressNginxEngine()
    assert not en.execute_host_routing_topology([], "h", "p").is_ok()

# ---------------------------------------------------------
# ENGINE 6: OmniElasticsearchLuceneQueryEngine
# ---------------------------------------------------------
def test_es_lucene_diagnostics():
    en = OmniElasticsearchLuceneQueryEngine()
    assert en.diagnostics()["status"] == "operational"

def test_es_lucene_valid():
    en = OmniElasticsearchLuceneQueryEngine(100)
    res = en.compute_token_matching_score("hello hello world", "hello omni")
    assert res.is_ok()
    out = res.unwrap()
    assert "hello" in out["matched_token_intersections"]
    assert out["algebraic_tf_score"] == 2.0 # TF=2

def test_es_lucene_exceeded_tokens():
    en = OmniElasticsearchLuceneQueryEngine(2)
    assert not en.compute_token_matching_score("one two three", "one").is_ok()

def test_es_lucene_no_match():
    en = OmniElasticsearchLuceneQueryEngine(100)
    res = en.compute_token_matching_score("hello world", "omni")
    assert res.unwrap()["algebraic_tf_score"] == 0.0

def test_es_lucene_empty():
    en = OmniElasticsearchLuceneQueryEngine()
    assert not en.compute_token_matching_score("", "h").is_ok()

# ---------------------------------------------------------
# ENGINE 7: OmniRedisPubsubChannelEngine
# ---------------------------------------------------------
def test_redis_pubsub_diagnostics():
    en = OmniRedisPubsubChannelEngine()
    assert en.diagnostics()["status"] == "operational"

def test_redis_pubsub_valid():
    en = OmniRedisPubsubChannelEngine(100)
    channels = {"ch1": ["s1", "s2"]}
    msgs = [{"publish_to": "ch1"}]
    res = en.calculate_message_fanout_distribution(channels, msgs)
    assert res.is_ok()
    out = res.unwrap()
    assert out["total_fanout_deliveries_executed"] == 2
    assert out["active_channel_hit_distribution"]["ch1"] == 1

def test_redis_pubsub_dead_letter():
    en = OmniRedisPubsubChannelEngine(100)
    channels = {"ch1": ["s1"]}
    msgs = [{"publish_to": "ch2"}]
    res = en.calculate_message_fanout_distribution(channels, msgs)
    assert res.unwrap()["dead_letter_unrouted_messages"] == 1

def test_redis_pubsub_exceeded_subs():
    en = OmniRedisPubsubChannelEngine(1)
    channels = {"ch1": ["s1", "s2"]}
    assert not en.calculate_message_fanout_distribution(channels, [{"publish_to": "ch1"}]).is_ok()

def test_redis_pubsub_empty():
    en = OmniRedisPubsubChannelEngine()
    assert not en.calculate_message_fanout_distribution({}, []).is_ok()

# ---------------------------------------------------------
# ENGINE 8: OmniPrometheusMetricsScraperEngine
# ---------------------------------------------------------
def test_prometheus_diagnostics():
    en = OmniPrometheusMetricsScraperEngine()
    assert en.diagnostics()["status"] == "operational"

def test_prometheus_valid():
    en = OmniPrometheusMetricsScraperEngine(10)
    lines = ["http_req{m=\"x\"} 10.5", "http_req{m=\"y\"} 5.5", "# comment"]
    res = en.parse_time_series_metric_payload(lines)
    assert res.is_ok()
    out = res.unwrap()
    assert out["total_aggregated_numerical_sum"] == 16.0
    assert out["valid_metrics_extracted"] == 2
    assert "http_req" in out["unique_metric_keys_parsed"]

def test_prometheus_invalid_math():
    en = OmniPrometheusMetricsScraperEngine(10)
    lines = ["http_req badval"]
    res = en.parse_time_series_metric_payload(lines)
    assert res.unwrap()["invalid_metric_formats"] == 1

def test_prometheus_exceeded():
    en = OmniPrometheusMetricsScraperEngine(1)
    assert not en.parse_time_series_metric_payload(["h 1", "h 2"]).is_ok()

def test_prometheus_empty():
    en = OmniPrometheusMetricsScraperEngine()
    assert not en.parse_time_series_metric_payload([]).is_ok()

# ---------------------------------------------------------
# ENGINE 9: OmniDockerSwarmOrchestratorEngine
# ---------------------------------------------------------
def test_docker_swarm_diagnostics():
    en = OmniDockerSwarmOrchestratorEngine()
    assert en.diagnostics()["status"] == "operational"

def test_docker_swarm_valid():
    en = OmniDockerSwarmOrchestratorEngine(10)
    # 5 replicas across 2 nodes -> node1 gets 3, node2 gets 2
    res = en.evaluate_replica_distribution_matrix(["n1", "n2"], 5)
    assert res.is_ok()
    out = res.unwrap()
    assert out["calculated_distribution_matrix"]["n1"] == 3
    assert out["calculated_distribution_matrix"]["n2"] == 2

def test_docker_swarm_exceeded():
    en = OmniDockerSwarmOrchestratorEngine(1)
    assert not en.evaluate_replica_distribution_matrix(["n1", "n2"], 5).is_ok()

def test_docker_swarm_negative_replicas():
    en = OmniDockerSwarmOrchestratorEngine(10)
    assert not en.evaluate_replica_distribution_matrix(["n1"], -5).is_ok()

def test_docker_swarm_empty():
    en = OmniDockerSwarmOrchestratorEngine()
    assert not en.evaluate_replica_distribution_matrix([], 5).is_ok()

# ---------------------------------------------------------
# ENGINE 10: OmniAngularRxjsObservableEngine
# ---------------------------------------------------------
def test_angular_rxjs_diagnostics():
    en = OmniAngularRxjsObservableEngine()
    assert en.diagnostics()["status"] == "operational"

def test_angular_rxjs_valid():
    en = OmniAngularRxjsObservableEngine(10)
    # Stream: [0, 1, 2, 3]
    # Filter > 0: [1, 2, 3]
    # Map * 2: [2, 4, 6]
    res = en.execute_rxjs_pipe_transformation([0, 1, 2, 3], [2])
    assert res.is_ok()
    out = res.unwrap()
    assert out["events_filtered"] == 1
    assert out["final_transformed_sequence"] == [2, 4, 6]

def test_angular_rxjs_exceeded():
    en = OmniAngularRxjsObservableEngine(2)
    assert not en.execute_rxjs_pipe_transformation([1, 2, 3], [1]).is_ok()

def test_angular_rxjs_multiple_maps():
    en = OmniAngularRxjsObservableEngine(10)
    res = en.execute_rxjs_pipe_transformation([5], [2, 10]) # 5 * 2 * 10
    assert res.unwrap()["final_transformed_sequence"] == [100]

def test_angular_rxjs_empty():
    en = OmniAngularRxjsObservableEngine()
    assert not en.execute_rxjs_pipe_transformation([], []).is_ok()

