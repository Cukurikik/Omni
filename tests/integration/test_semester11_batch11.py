import pytest
from src.compute.python_core.omni_electron_app_builder_engine import OmniElectronAppBuilderEngine
from src.compute.python_core.omni_pytorch_diffusion_model_engine import OmniPytorchDiffusionModelEngine
from src.compute.python_core.omni_stripe_payment_checkout_engine import OmniStripePaymentCheckoutEngine
from src.compute.python_core.omni_nginx_load_balancer_engine import OmniNginxLoadBalancerEngine
from src.compute.python_core.omni_nextjs_seo_optimization_engine import OmniNextjsSeoOptimizationEngine
from src.compute.python_core.omni_redis_cache_lru_engine import OmniRedisCacheLruEngine
from src.compute.python_core.omni_apollo_graphql_schema_engine import OmniApolloGraphqlSchemaEngine
from src.compute.python_core.omni_terraform_infrastructure_engine import OmniTerraformInfrastructureEngine
from src.compute.python_core.omni_opencv_face_tracking_engine import OmniOpencvFaceTrackingEngine
from src.compute.python_core.omni_flutter_state_riverpod_engine import OmniFlutterStateRiverpodEngine

# ---------------------------------------------------------
# ENGINE 1: OmniElectronAppBuilderEngine
# ---------------------------------------------------------
def test_electron_app_builder_diagnostics():
    en = OmniElectronAppBuilderEngine()
    assert en.diagnostics()["status"] == "operational"

def test_electron_app_builder_valid():
    en = OmniElectronAppBuilderEngine(100.0)
    assets = [{"name": "app.js", "size_mb": 10.0}, {"name": "img.png", "size_mb": 5.5}]
    res = en.compute_bundle_structural_metrics(assets)
    assert res.is_ok()
    out = res.unwrap()
    assert out["build_environment_validated"] is True
    assert out["total_computed_size_mb"] == 15.5

def test_electron_app_builder_exceeded():
    en = OmniElectronAppBuilderEngine(50.0)
    assets = [{"name": "video.mp4", "size_mb": 60.0}]
    res = en.compute_bundle_structural_metrics(assets)
    assert res.is_ok()
    assert res.unwrap()["build_environment_validated"] is False
    assert "video.mp4" in res.unwrap()["large_file_warnings"]

def test_electron_app_builder_negative_size():
    en = OmniElectronAppBuilderEngine()
    assert not en.compute_bundle_structural_metrics([{"name": "x", "size_mb": -5.0}]).is_ok()

def test_electron_app_builder_empty():
    en = OmniElectronAppBuilderEngine()
    assert not en.compute_bundle_structural_metrics([]).is_ok()

# ---------------------------------------------------------
# ENGINE 2: OmniPytorchDiffusionModelEngine
# ---------------------------------------------------------
def test_pytorch_diffusion_diagnostics():
    en = OmniPytorchDiffusionModelEngine()
    assert en.diagnostics()["status"] == "operational"

def test_pytorch_diffusion_valid():
    en = OmniPytorchDiffusionModelEngine(100)
    # decay approx e^(-0.01 * 10) = e^(-0.1) = ~0.90483
    res = en.execute_noise_vector_decay([1.0, 0.5], 10)
    assert res.is_ok()
    out = res.unwrap()
    assert out["tensor_dimensions_metric"] == 2
    assert out["applied_decay_factor"] > 0.9  # Loose math assertion

def test_pytorch_diffusion_exceeded():
    en = OmniPytorchDiffusionModelEngine(50)
    assert not en.execute_noise_vector_decay([1.0], 100).is_ok()

def test_pytorch_diffusion_negative_steps():
    en = OmniPytorchDiffusionModelEngine()
    assert not en.execute_noise_vector_decay([1.0], -5).is_ok()

def test_pytorch_diffusion_empty():
    en = OmniPytorchDiffusionModelEngine()
    assert not en.execute_noise_vector_decay([], 10).is_ok()

# ---------------------------------------------------------
# ENGINE 3: OmniStripePaymentCheckoutEngine
# ---------------------------------------------------------
def test_stripe_checkout_diagnostics():
    en = OmniStripePaymentCheckoutEngine()
    assert en.diagnostics()["status"] == "operational"

def test_stripe_checkout_valid():
    en = OmniStripePaymentCheckoutEngine(0.029, 0.30)
    # 100 * 0.029 + 0.30 = 2.9 + 0.30 = 3.2. Net = 96.8
    res = en.mathematical_calculate_gross_profit([{"amount": 100.0}])
    assert res.is_ok()
    out = res.unwrap()
    assert out["algebraic_computed_fees"] == 3.2
    assert out["algebraic_net_profit"] == 96.8

def test_stripe_checkout_invalid_negative():
    en = OmniStripePaymentCheckoutEngine()
    res = en.mathematical_calculate_gross_profit([{"amount": 100.0}, {"amount": -50.0}])
    assert res.is_ok() # Skips negatives
    assert 1 in res.unwrap()["invalid_transaction_indices"]

def test_stripe_checkout_missing_key():
    en = OmniStripePaymentCheckoutEngine()
    assert not en.mathematical_calculate_gross_profit([{"foo": 100}]).is_ok()

def test_stripe_checkout_empty():
    en = OmniStripePaymentCheckoutEngine()
    assert not en.mathematical_calculate_gross_profit([]).is_ok()

# ---------------------------------------------------------
# ENGINE 4: OmniNginxLoadBalancerEngine
# ---------------------------------------------------------
def test_nginx_load_balancer_diagnostics():
    en = OmniNginxLoadBalancerEngine()
    assert en.diagnostics()["status"] == "operational"

def test_nginx_load_balancer_valid():
    en = OmniNginxLoadBalancerEngine(["node-1", "node-2"])
    reqs = ["userA", "userB", "userC", "userD"]
    res = en.calculate_round_robin_distribution(reqs)
    assert res.is_ok()
    out = res.unwrap()
    assert out["backend_nodes_count"] == 2
    assert out["total_traffic_evaluated"] == 4
    assert out["is_load_distributed"] is True

def test_nginx_load_balancer_no_nodes():
    en = OmniNginxLoadBalancerEngine([])
    # Will fail via internal constraints
    assert not en.calculate_round_robin_distribution(["req1"]).is_ok()

def test_nginx_load_balancer_invalid_type():
    en = OmniNginxLoadBalancerEngine(["node-1"])
    assert not en.calculate_round_robin_distribution([123]).is_ok()

def test_nginx_load_balancer_empty_requests():
    en = OmniNginxLoadBalancerEngine(["node-1"])
    assert not en.calculate_round_robin_distribution([]).is_ok()

# ---------------------------------------------------------
# ENGINE 5: OmniNextjsSeoOptimizationEngine
# ---------------------------------------------------------
def test_nextjs_seo_diagnostics():
    en = OmniNextjsSeoOptimizationEngine()
    assert en.diagnostics()["status"] == "operational"

def test_nextjs_seo_valid():
    en = OmniNextjsSeoOptimizationEngine(60, 160)
    res = en.calculate_seo_metadata_geometries({"title": "Good", "description": "Also good"})
    assert res.is_ok()
    assert res.unwrap()["is_search_optimized_structurally"] is True

def test_nextjs_seo_title_exceeded():
    en = OmniNextjsSeoOptimizationEngine(5, 100)
    res = en.calculate_seo_metadata_geometries({"title": "Too Long Title", "description": "Good"})
    assert res.unwrap()["is_search_optimized_structurally"] is False
    assert "TITLE_BOUNDS_VIOLATION" in res.unwrap()["violations_flagged"]

def test_nextjs_seo_missing_keys():
    en = OmniNextjsSeoOptimizationEngine()
    assert not en.calculate_seo_metadata_geometries({"title": "OK"}).is_ok()

def test_nextjs_seo_empty():
    en = OmniNextjsSeoOptimizationEngine()
    assert not en.calculate_seo_metadata_geometries({}).is_ok()

# ---------------------------------------------------------
# ENGINE 6: OmniRedisCacheLruEngine
# ---------------------------------------------------------
def test_redis_lru_diagnostics():
    en = OmniRedisCacheLruEngine()
    assert en.diagnostics()["status"] == "operational"

def test_redis_lru_valid():
    en = OmniRedisCacheLruEngine(2)
    ops = [
        {"op": "SET", "key": "A", "val": 1},
        {"op": "SET", "key": "B", "val": 2},
        {"op": "GET", "key": "A"}, # Moves A to recent
        {"op": "SET", "key": "C", "val": 3} # Evicts B
    ]
    res = en.execute_lru_cache_math_trace(ops)
    assert res.is_ok()
    out = res.unwrap()
    assert out["cache_geometric_size"] == 2
    assert "B" in out["evicted_lru_keys"]
    assert "A" in out["currently_stored_keys"]
    assert "C" in out["currently_stored_keys"]

def test_redis_lru_invalid_instruction():
    en = OmniRedisCacheLruEngine(5)
    assert not en.execute_lru_cache_math_trace([{"op": "DELETE", "key": "A"}]).is_ok()

def test_redis_lru_missing_keys():
    en = OmniRedisCacheLruEngine()
    assert not en.execute_lru_cache_math_trace([{"op": "SET"}]).is_ok()

def test_redis_lru_empty():
    en = OmniRedisCacheLruEngine()
    assert not en.execute_lru_cache_math_trace([]).is_ok()

# ---------------------------------------------------------
# ENGINE 7: OmniApolloGraphqlSchemaEngine
# ---------------------------------------------------------
def test_apollo_graphql_diagnostics():
    en = OmniApolloGraphqlSchemaEngine()
    assert en.diagnostics()["status"] == "operational"

def test_apollo_graphql_valid():
    en = OmniApolloGraphqlSchemaEngine()
    schema = {
        "User": {"id": "ID!", "name": "String", "posts": "[Post!]!"},
        "Post": {"title": "String", "author": "User"}
    }
    res = en.validate_schema_field_topologies(schema)
    assert res.is_ok()
    assert res.unwrap()["is_schema_topologically_compliant"] is True

def test_apollo_graphql_invalid():
    en = OmniApolloGraphqlSchemaEngine()
    schema = {"User": {"id": "ID", "unknown": "UnknownType"}}
    res = en.validate_schema_field_topologies(schema)
    assert res.unwrap()["is_schema_topologically_compliant"] is False
    assert "User.unknown -> UnknownType" in res.unwrap()["invalid_field_resolutions"]

def test_apollo_graphql_non_dict_fields():
    en = OmniApolloGraphqlSchemaEngine()
    schema = {"User": "String"} # Should be dict
    assert not en.validate_schema_field_topologies(schema).is_ok()

def test_apollo_graphql_empty():
    en = OmniApolloGraphqlSchemaEngine()
    assert not en.validate_schema_field_topologies({}).is_ok()

# ---------------------------------------------------------
# ENGINE 8: OmniTerraformInfrastructureEngine
# ---------------------------------------------------------
def test_terraform_infra_diagnostics():
    en = OmniTerraformInfrastructureEngine()
    assert en.diagnostics()["status"] == "operational"

def test_terraform_infra_valid():
    en = OmniTerraformInfrastructureEngine(10)
    rescs = [
        {"type": "aws_vpc", "id": "main"},
        {"type": "aws_instance", "id": "web1", "depends_on": ["aws_vpc.main"]}
    ]
    res = en.compile_hcl_resource_graph(rescs)
    assert res.is_ok()
    out = res.unwrap()
    assert "aws_vpc.main" in out["standalone_root_resources"]
    assert "aws_instance.web1" in out["dependent_leaf_resources"]

def test_terraform_infra_exceeded():
    en = OmniTerraformInfrastructureEngine(1)
    rescs = [{"type": "aws_vpc", "id": "main"}, {"type": "aws_instance", "id": "web"}]
    assert not en.compile_hcl_resource_graph(rescs).is_ok()

def test_terraform_infra_missing_keys():
    en = OmniTerraformInfrastructureEngine()
    assert not en.compile_hcl_resource_graph([{"type": "aws_vpc"}]).is_ok()

def test_terraform_infra_empty():
    en = OmniTerraformInfrastructureEngine()
    assert not en.compile_hcl_resource_graph([]).is_ok()

# ---------------------------------------------------------
# ENGINE 9: OmniOpencvFaceTrackingEngine
# ---------------------------------------------------------
def test_opencv_tracking_diagnostics():
    en = OmniOpencvFaceTrackingEngine()
    assert en.diagnostics()["status"] == "operational"

def test_opencv_tracking_valid_movement():
    en = OmniOpencvFaceTrackingEngine(10.0)
    # Moved 10 right, 10 down. Euclidean is sqrt(200) = ~14.14 (> 10)
    prev = [{"id": 1, "x": 0, "y": 0}]
    cur = [{"id": 1, "x": 10, "y": 10}]
    res = en.track_bounding_box_logic(prev, cur)
    assert res.is_ok()
    out = res.unwrap()
    assert 1 in out["faces_in_motion"]
    assert out["euclidean_distance_matrix"][1] == 14.14

def test_opencv_tracking_no_movement():
    en = OmniOpencvFaceTrackingEngine(20.0)
    prev = [{"id": 1, "x": 0, "y": 0}]
    cur = [{"id": 1, "x": 5, "y": 0}] # Moved 5, threshold is 20
    res = en.track_bounding_box_logic(prev, cur)
    assert 1 not in res.unwrap()["faces_in_motion"]

def test_opencv_tracking_missing_coords():
    en = OmniOpencvFaceTrackingEngine()
    assert not en.track_bounding_box_logic([{"id": 1}], [{"id": 1, "x": 0, "y": 0}]).is_ok()

def test_opencv_tracking_empty():
    en = OmniOpencvFaceTrackingEngine()
    assert not en.track_bounding_box_logic([], []).is_ok()

# ---------------------------------------------------------
# ENGINE 10: OmniFlutterStateRiverpodEngine
# ---------------------------------------------------------
def test_flutter_riverpod_diagnostics():
    en = OmniFlutterStateRiverpodEngine()
    assert en.diagnostics()["status"] == "operational"

def test_flutter_riverpod_valid():
    en = OmniFlutterStateRiverpodEngine(10)
    state = {"count": 1}
    actions = [{"target": "count", "instruction": "ADD", "val": 2}]
    res = en.execute_state_rebuild_events(state, actions)
    assert res.is_ok()
    out = res.unwrap()
    assert out["final_state_graph_dimension"]["count"] == 3
    assert out["total_rebuild_events_fired"] == 1

def test_flutter_riverpod_new_state():
    en = OmniFlutterStateRiverpodEngine(10)
    state = {}
    actions = [{"target": "theme", "instruction": "SET", "val": "dark"}]
    res = en.execute_state_rebuild_events(state, actions)
    assert res.unwrap()["final_state_graph_dimension"]["theme"] == "dark"

def test_flutter_riverpod_missing_instruction():
    en = OmniFlutterStateRiverpodEngine()
    assert not en.execute_state_rebuild_events({}, [{"target": "a"}]).is_ok()

def test_flutter_riverpod_exceeded():
    en = OmniFlutterStateRiverpodEngine(1)
    actions = [{"target": "a", "instruction": "SET", "val": 1}, {"target": "b", "instruction": "SET", "val": 2}]
    assert not en.execute_state_rebuild_events({}, actions).is_ok()

