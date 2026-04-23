import pytest
from src.compute.python_core.omni_express_middleware_router_engine import OmniExpressMiddlewareRouterEngine
from src.compute.python_core.omni_kubernetes_helm_chart_engine import OmniKubernetesHelmChartEngine
from src.compute.python_core.omni_nestjs_dependency_injection_engine import OmniNestjsDependencyInjectionEngine
from src.compute.python_core.omni_pandas_dataframe_aggregator_engine import OmniPandasDataframeAggregatorEngine
from src.compute.python_core.omni_redis_cluster_sharding_engine import OmniRedisClusterShardingEngine
from src.compute.python_core.omni_django_q_task_queue_engine import OmniDjangoQTaskQueueEngine
from src.compute.python_core.omni_tensorflow_keras_optimizer_engine import OmniTensorflowKerasOptimizerEngine
from src.compute.python_core.omni_aws_s3_bucket_policy_engine import OmniAwsS3BucketPolicyEngine
from src.compute.python_core.omni_react_query_caching_engine import OmniReactQueryCachingEngine
from src.compute.python_core.omni_go_gin_rest_api_engine import OmniGoGinRestApiEngine

# ---------------------------------------------------------
# ENGINE 1: OmniExpressMiddlewareRouterEngine
# ---------------------------------------------------------
def test_express_router_diagnostics():
    en = OmniExpressMiddlewareRouterEngine()
    assert en.diagnostics()["status"] == "operational"

def test_express_router_valid():
    en = OmniExpressMiddlewareRouterEngine(10)
    stack = ["logger", "parser", "handler"]
    res = en.execute_middleware_execution_trace(stack, {"data": 1})
    assert res.is_ok()
    out = res.unwrap()
    assert out["middleware_layers_executed"] == 3
    assert out["chain_halted_early_at"] is None
    assert "parsed" in out["final_request_state_matrix"]

def test_express_router_auth_halt():
    en = OmniExpressMiddlewareRouterEngine(10)
    stack = ["logger", "auth", "handler"]
    res = en.execute_middleware_execution_trace(stack, {"data": 1})
    assert res.is_ok()
    out = res.unwrap()
    assert out["chain_halted_early_at"] == "auth"
    assert out["middleware_layers_executed"] == 2

def test_express_router_exceeded():
    en = OmniExpressMiddlewareRouterEngine(1)
    assert not en.execute_middleware_execution_trace(["a", "b"], {}).is_ok()

def test_express_router_empty():
    en = OmniExpressMiddlewareRouterEngine()
    assert not en.execute_middleware_execution_trace([], {}).is_ok()

# ---------------------------------------------------------
# ENGINE 2: OmniKubernetesHelmChartEngine
# ---------------------------------------------------------
def test_helm_chart_diagnostics():
    en = OmniKubernetesHelmChartEngine()
    assert en.diagnostics()["status"] == "operational"

def test_helm_chart_valid():
    en = OmniKubernetesHelmChartEngine(10)
    base = {"web": {"port": 80, "img": "a"}}
    ov = [{"web": {"port": 8080}}]
    res = en.compute_values_yaml_override_hierarchy(base, ov)
    assert res.is_ok()
    out = res.unwrap()
    assert out["merged_values_matrix"]["web"]["port"] == 8080
    assert out["distinct_keys_overridden_structurally"] == 1

def test_helm_chart_exceeded():
    en = OmniKubernetesHelmChartEngine(1)
    assert not en.compute_values_yaml_override_hierarchy({"a": 1}, [{"a": 2}, {"a": 3}]).is_ok()

def test_helm_chart_multiple_layers():
    en = OmniKubernetesHelmChartEngine(10)
    base = {"web": {"port": 80}}
    ov = [{"web": {"img": "b"}}, {"web": {"port": 443}}]
    res = en.compute_values_yaml_override_hierarchy(base, ov)
    assert res.unwrap()["merged_values_matrix"]["web"]["port"] == 443
    assert res.unwrap()["merged_values_matrix"]["web"]["img"] == "b"

def test_helm_chart_empty():
    en = OmniKubernetesHelmChartEngine()
    assert not en.compute_values_yaml_override_hierarchy({}, []).is_ok()

# ---------------------------------------------------------
# ENGINE 3: OmniNestjsDependencyInjectionEngine
# ---------------------------------------------------------
def test_nestjs_di_diagnostics():
    en = OmniNestjsDependencyInjectionEngine()
    assert en.diagnostics()["status"] == "operational"

def test_nestjs_di_valid():
    en = OmniNestjsDependencyInjectionEngine(10)
    providers = [{"name": "Auth", "inject": ["User"]}, {"name": "User"}]
    res = en.validate_provider_graph_topology(providers)
    assert res.is_ok()
    assert res.unwrap()["is_graph_acyclic"] is True

def test_nestjs_di_cyclic():
    en = OmniNestjsDependencyInjectionEngine(10)
    providers = [{"name": "A", "inject": ["B"]}, {"name": "B", "inject": ["A"]}]
    res = en.validate_provider_graph_topology(providers)
    assert res.is_ok()
    assert res.unwrap()["is_graph_acyclic"] is False
    assert res.unwrap()["cyclical_dependency_detected"] is not None

def test_nestjs_di_exceeded():
    en = OmniNestjsDependencyInjectionEngine(1)
    assert not en.validate_provider_graph_topology([{"name": "A"}, {"name": "B"}]).is_ok()

def test_nestjs_di_empty():
    en = OmniNestjsDependencyInjectionEngine()
    assert not en.validate_provider_graph_topology([]).is_ok()

# ---------------------------------------------------------
# ENGINE 4: OmniPandasDataframeAggregatorEngine
# ---------------------------------------------------------
def test_pandas_aggregator_diagnostics():
    en = OmniPandasDataframeAggregatorEngine()
    assert en.diagnostics()["status"] == "operational"

def test_pandas_aggregator_valid():
    en = OmniPandasDataframeAggregatorEngine(10)
    rows = [{"cat": "A", "val": 10}, {"cat": "A", "val": 20}, {"cat": "B", "val": 5}]
    res = en.compute_groupby_summation_matrix(rows, "cat", "val")
    assert res.is_ok()
    out = res.unwrap()
    assert out["aggregated_sum_matrix"]["A"] == 30.0
    assert out["aggregated_sum_matrix"]["B"] == 5.0

def test_pandas_aggregator_missing_keys():
    en = OmniPandasDataframeAggregatorEngine(10)
    rows = [{"cat": "A", "val": 10}, {"cat": "A"}]
    res = en.compute_groupby_summation_matrix(rows, "cat", "val")
    assert res.unwrap()["rows_with_missing_keys"] == 1
    assert res.unwrap()["aggregated_sum_matrix"]["A"] == 10.0

def test_pandas_aggregator_exceeded():
    en = OmniPandasDataframeAggregatorEngine(1)
    assert not en.compute_groupby_summation_matrix([{"c":"A","v":1}, {"c":"B","v":2}], "c", "v").is_ok()

def test_pandas_aggregator_empty():
    en = OmniPandasDataframeAggregatorEngine()
    assert not en.compute_groupby_summation_matrix(None, "c", "v").is_ok()

# ---------------------------------------------------------
# ENGINE 5: OmniRedisClusterShardingEngine
# ---------------------------------------------------------
def test_redis_sharding_diagnostics():
    en = OmniRedisClusterShardingEngine()
    assert en.diagnostics()["status"] == "operational"

def test_redis_sharding_valid():
    en = OmniRedisClusterShardingEngine(100)
    res = en.calculate_crc16_hash_slot_distribution(["k1", "k2", "k3"], 3)
    assert res.is_ok()
    out = res.unwrap()
    assert out["keys_processed"] == 3
    assert out["cluster_shards_available"] == 3
    assert len(out["calculated_key_slot_matrix"]) == 3

def test_redis_sharding_zero_nodes():
    en = OmniRedisClusterShardingEngine(100)
    assert not en.calculate_crc16_hash_slot_distribution(["k1"], 0).is_ok()

def test_redis_sharding_exceeded():
    en = OmniRedisClusterShardingEngine(1)
    assert not en.calculate_crc16_hash_slot_distribution(["k1", "k2"], 3).is_ok()

def test_redis_sharding_empty():
    en = OmniRedisClusterShardingEngine()
    assert not en.calculate_crc16_hash_slot_distribution([], 3).is_ok()

# ---------------------------------------------------------
# ENGINE 6: OmniDjangoQTaskQueueEngine
# ---------------------------------------------------------
def test_django_q_diagnostics():
    en = OmniDjangoQTaskQueueEngine()
    assert en.diagnostics()["status"] == "operational"

def test_django_q_valid():
    en = OmniDjangoQTaskQueueEngine(10)
    # p=5 (high), p=1 (low)
    tasks = [{"task_id": "1", "priority": 1, "created_at_ms": 100}, 
             {"task_id": "2", "priority": 5, "created_at_ms": 150}]
    res = en.compute_priority_scheduling_matrix(tasks)
    assert res.is_ok()
    out = res.unwrap()
    assert out["ordered_execution_sequence"] == ["2", "1"]

def test_django_q_tie_breaker():
    en = OmniDjangoQTaskQueueEngine(10)
    tasks = [{"task_id": "1", "priority": 5, "created_at_ms": 200}, 
             {"task_id": "2", "priority": 5, "created_at_ms": 100}] # earlier wins
    res = en.compute_priority_scheduling_matrix(tasks)
    assert res.unwrap()["ordered_execution_sequence"] == ["2", "1"]

def test_django_q_exceeded():
    en = OmniDjangoQTaskQueueEngine(1)
    assert not en.compute_priority_scheduling_matrix([{"task_id": "1", "priority": 1, "created_at_ms": 10},
                                                      {"task_id": "2", "priority": 2, "created_at_ms": 20}]).is_ok()

def test_django_q_empty():
    en = OmniDjangoQTaskQueueEngine()
    assert not en.compute_priority_scheduling_matrix(None).is_ok()

# ---------------------------------------------------------
# ENGINE 7: OmniTensorflowKerasOptimizerEngine
# ---------------------------------------------------------
def test_tf_optimizer_diagnostics():
    en = OmniTensorflowKerasOptimizerEngine()
    assert en.diagnostics()["status"] == "operational"

def test_tf_optimizer_valid():
    en = OmniTensorflowKerasOptimizerEngine(10)
    # W = 0.5 - (0.1 * 1.0) = 0.4. Next W = 0.4 - (0.1 * 1.0) = 0.3
    res = en.compute_sgd_gradient_step_simulation(initial_weight=0.5, learning_rate=0.1, gradients=[1.0, 1.0])
    assert res.is_ok()
    out = res.unwrap()
    assert out["final_updated_weight"] == 0.3
    assert len(out["weight_trajectory_matrix"]) == 3

def test_tf_optimizer_exceeded():
    en = OmniTensorflowKerasOptimizerEngine(1)
    assert not en.compute_sgd_gradient_step_simulation(0.5, 0.1, [1.0, 1.0]).is_ok()

def test_tf_optimizer_negative_grad():
    en = OmniTensorflowKerasOptimizerEngine(10)
    res = en.compute_sgd_gradient_step_simulation(0.1, 0.1, [-1.0])
    # 0.1 - (0.1 * -1.0) = 0.2
    assert res.unwrap()["final_updated_weight"] == 0.2

def test_tf_optimizer_empty():
    en = OmniTensorflowKerasOptimizerEngine()
    assert not en.compute_sgd_gradient_step_simulation(0.5, 0.1, None).is_ok()

# ---------------------------------------------------------
# ENGINE 8: OmniAwsS3BucketPolicyEngine
# ---------------------------------------------------------
def test_s3_policy_diagnostics():
    en = OmniAwsS3BucketPolicyEngine()
    assert en.diagnostics()["status"] == "operational"

def test_s3_policy_allow_valid():
    en = OmniAwsS3BucketPolicyEngine(10)
    stmt = [{"Effect": "Allow", "Action": ["s3:Get*"], "Resource": ["*"]}]
    res = en.evaluate_iam_policy_allow_deny_math(stmt, "s3:GetObject", "arn:aws:s3:::b/obj")
    assert res.is_ok()
    assert res.unwrap()["final_authorization_decision"] is True

def test_s3_policy_explicit_deny():
    en = OmniAwsS3BucketPolicyEngine(10)
    stmt = [{"Effect": "Allow", "Action": ["*"], "Resource": ["*"]},
            {"Effect": "Deny", "Action": ["s3:DeleteObject"], "Resource": ["*"]}]
    res = en.evaluate_iam_policy_allow_deny_math(stmt, "s3:DeleteObject", "arn")
    assert res.unwrap()["final_authorization_decision"] is False
    assert res.unwrap()["explicit_deny_triggered"] is True

def test_s3_policy_exceeded():
    en = OmniAwsS3BucketPolicyEngine(1)
    stmt = [{"Effect": "Allow", "Action": [], "Resource": []}, {"Effect": "Deny", "Action": [], "Resource": []}]
    assert not en.evaluate_iam_policy_allow_deny_math(stmt, "A", "B").is_ok()

def test_s3_policy_empty():
    en = OmniAwsS3BucketPolicyEngine()
    assert not en.evaluate_iam_policy_allow_deny_math([], "A", "B").is_ok()

# ---------------------------------------------------------
# ENGINE 9: OmniReactQueryCachingEngine
# ---------------------------------------------------------
def test_react_query_diagnostics():
    en = OmniReactQueryCachingEngine()
    assert en.diagnostics()["status"] == "operational"

def test_react_query_valid():
    en = OmniReactQueryCachingEngine(10)
    # query1 stale time 500, updated at 1000. Current is 1600. Diff=600 >= 500 -> Stale
    # query2 stale time 500, updated at 1200. Diff=400 < 500 -> Fresh
    cache = {
        "q1": {"updated_at_ms": 1000, "stale_time_ms": 500},
        "q2": {"updated_at_ms": 1200, "stale_time_ms": 500}
    }
    res = en.execute_temporal_stale_invalidation(cache, 1600)
    assert res.is_ok()
    out = res.unwrap()
    assert out["stale_invalidated_keys_count"] == 1
    assert out["fresh_valid_keys_count"] == 1
    assert "q1" in out["stale_query_keys_matrix"]

def test_react_query_exceeded():
    en = OmniReactQueryCachingEngine(1)
    cache = {"q1": {"updated_at_ms": 1, "stale_time_ms": 1}, "q2": {"updated_at_ms": 1, "stale_time_ms": 1}}
    assert not en.execute_temporal_stale_invalidation(cache, 10).is_ok()

def test_react_query_negative_time():
    en = OmniReactQueryCachingEngine(10)
    assert not en.execute_temporal_stale_invalidation({"q1":{}}, -10).is_ok()

def test_react_query_empty():
    en = OmniReactQueryCachingEngine()
    assert not en.execute_temporal_stale_invalidation(None, 100).is_ok()

# ---------------------------------------------------------
# ENGINE 10: OmniGoGinRestApiEngine
# ---------------------------------------------------------
def test_go_gin_diagnostics():
    en = OmniGoGinRestApiEngine()
    assert en.diagnostics()["status"] == "operational"

def test_go_gin_valid():
    en = OmniGoGinRestApiEngine(10)
    routes = ["/users/:id", "/posts/:pid/comments/:cid"]
    res = en.evaluate_exact_path_parametric_routing(routes, "/users/123")
    assert res.is_ok()
    out = res.unwrap()
    assert out["was_route_matched"] is True
    assert out["matched_route_pattern"] == "/users/:id"
    assert out["extracted_path_parameters"]["id"] == "123"

def test_go_gin_no_match():
    en = OmniGoGinRestApiEngine(10)
    routes = ["/users/:id"]
    res = en.evaluate_exact_path_parametric_routing(routes, "/posts/123")
    assert res.unwrap()["was_route_matched"] is False

def test_go_gin_exceeded():
    en = OmniGoGinRestApiEngine(1)
    assert not en.evaluate_exact_path_parametric_routing(["/a", "/b"], "/x").is_ok()

def test_go_gin_empty():
    en = OmniGoGinRestApiEngine()
    assert not en.evaluate_exact_path_parametric_routing([], "/x").is_ok()

