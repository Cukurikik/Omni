import pytest
from src.compute.python_core.omni_django_polls_tutorial_engine import OmniDjangoPollsTutorialEngine
from src.compute.python_core.omni_threejs_particle_engine import OmniThreejsParticleEngine
from src.compute.python_core.omni_jwt_auth_middleware_engine import OmniJwtAuthMiddlewareEngine
from src.compute.python_core.omni_docker_compose_parser_engine import OmniDockerComposeParserEngine
from src.compute.python_core.omni_mern_ecommerce_cart_engine import OmniMernEcommerceCartEngine
from src.compute.python_core.omni_kubernetes_pod_scheduler_engine import OmniKubernetesPodSchedulerEngine
from src.compute.python_core.omni_rust_tokio_async_engine import OmniRustTokioAsyncEngine
from src.compute.python_core.omni_react_native_navigation_engine import OmniReactNativeNavigationEngine
from src.compute.python_core.omni_golang_gin_router_engine import OmniGolangGinRouterEngine
from src.compute.python_core.omni_python_fastapi_di_engine import OmniPythonFastapiDiEngine

# ---------------------------------------------------------
# ENGINE 1: OmniDjangoPollsTutorialEngine
# ---------------------------------------------------------
def test_django_polls_diagnostics():
    en = OmniDjangoPollsTutorialEngine()
    assert en.diagnostics()["status"] == "operational"

def test_django_polls_valid():
    en = OmniDjangoPollsTutorialEngine(1000)
    data = {"question": "Best Tech?", "choices": [{"text": "Python", "votes": 500}, {"text": "Rust", "votes": 300}]}
    res = en.execute_vote_computation_matrix(data)
    assert res.is_ok()
    out = res.unwrap()
    assert out["total_votes_tallied"] == 800
    assert out["winning_metric_geometry"] == "Python"
    assert out["max_vote_density"] == 500

def test_django_polls_limit_exceeded():
    en = OmniDjangoPollsTutorialEngine(500)
    data = {"choices": [{"votes": 600}]}
    assert not en.execute_vote_computation_matrix(data).is_ok()

def test_django_polls_negative_votes():
    en = OmniDjangoPollsTutorialEngine()
    data = {"choices": [{"votes": -10}]}
    assert not en.execute_vote_computation_matrix(data).is_ok()

def test_django_polls_empty_data():
    en = OmniDjangoPollsTutorialEngine()
    assert not en.execute_vote_computation_matrix({}).is_ok()

# ---------------------------------------------------------
# ENGINE 2: OmniThreejsParticleEngine
# ---------------------------------------------------------
def test_threejs_particle_diagnostics():
    en = OmniThreejsParticleEngine()
    assert en.diagnostics()["status"] == "operational"

def test_threejs_particle_valid_move():
    en = OmniThreejsParticleEngine(1000.0)
    particles = [{"id": 1, "x": 0, "y": 0, "z": 0}]
    res = en.compute_particle_physics_tick(particles, 10.5)
    assert res.is_ok()
    assert res.unwrap()["active_particles_remaining"] == 1

def test_threejs_particle_out_of_bounds():
    en = OmniThreejsParticleEngine(100.0)
    particles = [{"id": 42, "x": 95, "y": 0, "z": 0}]
    # 95 + 10 = 105 (> 100 limit)
    res = en.compute_particle_physics_tick(particles, 10.0)
    assert 42 in res.unwrap()["out_of_bounds_ids"]
    assert res.unwrap()["active_particles_remaining"] == 0

def test_threejs_particle_missing_axes():
    en = OmniThreejsParticleEngine()
    assert not en.compute_particle_physics_tick([{"x": 1}], 5.0).is_ok()

def test_threejs_particle_empty():
    en = OmniThreejsParticleEngine()
    assert not en.compute_particle_physics_tick([], 1.0).is_ok()

# ---------------------------------------------------------
# ENGINE 3: OmniJwtAuthMiddlewareEngine
# ---------------------------------------------------------
def test_jwt_auth_diagnostics():
    en = OmniJwtAuthMiddlewareEngine()
    assert en.diagnostics()["status"] == "operational"

def test_jwt_auth_valid_token():
    en = OmniJwtAuthMiddlewareEngine(3)
    res = en.mathematical_verify_token_geometry(["head.pyload.sig", "a.b.c"])
    assert res.is_ok()
    assert res.unwrap()["structurally_valid_tokens"] == 2
    assert res.unwrap()["secure_boundary_status"] == "LOCKED"

def test_jwt_auth_invalid_token():
    en = OmniJwtAuthMiddlewareEngine(3)
    res = en.mathematical_verify_token_geometry(["head.payload", "a.b.c"])
    assert res.unwrap()["invalid_topology_tokens"] == 1
    assert res.unwrap()["secure_boundary_status"] == "BREACHED"

def test_jwt_auth_non_string():
    en = OmniJwtAuthMiddlewareEngine()
    assert not en.mathematical_verify_token_geometry([123]).is_ok()

def test_jwt_auth_empty():
    en = OmniJwtAuthMiddlewareEngine()
    assert not en.mathematical_verify_token_geometry([]).is_ok()

# ---------------------------------------------------------
# ENGINE 4: OmniDockerComposeParserEngine
# ---------------------------------------------------------
def test_docker_compose_diagnostics():
    en = OmniDockerComposeParserEngine()
    assert en.diagnostics()["status"] == "operational"

def test_docker_compose_valid():
    en = OmniDockerComposeParserEngine(10)
    schema = {"version": "3", "services": {"web": {}, "db": {}}}
    res = en.execute_parse_compose_matrix(schema)
    assert res.is_ok()
    out = res.unwrap()
    assert out["total_services_mapped"] == 2
    assert out["contains_database_logic_node"] is True

def test_docker_compose_capacity_exceeded():
    en = OmniDockerComposeParserEngine(1)
    schema = {"services": {"s1": {}, "s2": {}}}
    assert not en.execute_parse_compose_matrix(schema).is_ok()

def test_docker_compose_missing_services():
    en = OmniDockerComposeParserEngine()
    assert not en.execute_parse_compose_matrix({"version": "3"}).is_ok()

def test_docker_compose_empty():
    en = OmniDockerComposeParserEngine()
    assert not en.execute_parse_compose_matrix({}).is_ok()

# ---------------------------------------------------------
# ENGINE 5: OmniMernEcommerceCartEngine
# ---------------------------------------------------------
def test_mern_cart_diagnostics():
    en = OmniMernEcommerceCartEngine()
    assert en.diagnostics()["status"] == "operational"

def test_mern_cart_valid():
    en = OmniMernEcommerceCartEngine(50)
    cart = [{"price": 10.0, "quantity": 2}, {"price": 5.0, "quantity": 3}]
    res = en.compute_cart_checkout_metrics(cart)
    assert res.is_ok()
    out = res.unwrap()
    assert out["gross_monetary_value"] == 35.0  # 20 + 15
    assert out["total_item_quantity"] == 5

def test_mern_cart_limit_exceeded():
    en = OmniMernEcommerceCartEngine(1) # array limit
    cart = [{"price": 10.0, "quantity": 1}, {"price": 5.0, "quantity": 1}]
    assert not en.compute_cart_checkout_metrics(cart).is_ok()

def test_mern_cart_negative_values():
    en = OmniMernEcommerceCartEngine()
    cart = [{"price": -10.0, "quantity": 1}]
    assert not en.compute_cart_checkout_metrics(cart).is_ok()

def test_mern_cart_null():
    en = OmniMernEcommerceCartEngine()
    assert not en.compute_cart_checkout_metrics(None).is_ok()

# ---------------------------------------------------------
# ENGINE 6: OmniKubernetesPodSchedulerEngine
# ---------------------------------------------------------
def test_k8s_scheduler_diagnostics():
    en = OmniKubernetesPodSchedulerEngine()
    assert en.diagnostics()["status"] == "operational"

def test_k8s_scheduler_valid():
    en = OmniKubernetesPodSchedulerEngine(2000)
    pods = [{"name": "p1", "cpu_m": 1000}, {"name": "p2", "cpu_m": 500}]
    res = en.map_pod_scheduling_constraints(pods)
    assert res.is_ok()
    assert "p1" in res.unwrap()["successfully_scheduled_pods"]
    assert "p2" in res.unwrap()["successfully_scheduled_pods"]

def test_k8s_scheduler_pending():
    en = OmniKubernetesPodSchedulerEngine(1000)
    pods = [{"name": "p1", "cpu_m": 800}, {"name": "p2", "cpu_m": 500}]
    res = en.map_pod_scheduling_constraints(pods)
    # p1 scheduled (800), p2 pending (500 > remainder 200)
    assert "p1" in res.unwrap()["successfully_scheduled_pods"]
    assert "p2" in res.unwrap()["pending_queue_pods"]

def test_k8s_scheduler_negative_cpu():
    en = OmniKubernetesPodSchedulerEngine()
    assert not en.map_pod_scheduling_constraints([{"name": "bad", "cpu_m": -100}]).is_ok()

def test_k8s_scheduler_empty():
    en = OmniKubernetesPodSchedulerEngine()
    assert not en.map_pod_scheduling_constraints([]).is_ok()

# ---------------------------------------------------------
# ENGINE 7: OmniRustTokioAsyncEngine
# ---------------------------------------------------------
def test_rust_tokio_diagnostics():
    en = OmniRustTokioAsyncEngine()
    assert en.diagnostics()["status"] == "operational"

def test_rust_tokio_valid_flow():
    en = OmniRustTokioAsyncEngine(2000)
    res = en.compute_async_event_timings([500, 1000])
    assert res.is_ok()
    assert res.unwrap()["successfully_resolved_events"] == 2
    assert res.unwrap()["total_duration_simulated_ms"] == 1500

def test_rust_tokio_timeout():
    en = OmniRustTokioAsyncEngine(1000)
    res = en.compute_async_event_timings([800, 300]) # 800 + 300 = 1100 > 1000
    assert res.unwrap()["successfully_resolved_events"] == 1
    assert res.unwrap()["timeout_dropped_events"] == 1

def test_rust_tokio_invalid_type():
    en = OmniRustTokioAsyncEngine()
    assert not en.compute_async_event_timings(["fast", "slow"]).is_ok()

def test_rust_tokio_empty():
    en = OmniRustTokioAsyncEngine()
    assert not en.compute_async_event_timings([]).is_ok()

# ---------------------------------------------------------
# ENGINE 8: OmniReactNativeNavigationEngine
# ---------------------------------------------------------
def test_react_native_nav_diagnostics():
    en = OmniReactNativeNavigationEngine()
    assert en.diagnostics()["status"] == "operational"

def test_react_native_nav_push_pop():
    en = OmniReactNativeNavigationEngine(5)
    actions = [{"type": "PUSH", "route": "A"}, {"type": "PUSH", "route": "B"}, {"type": "POP"}]
    res = en.execute_navigation_stack_matrix(actions)
    assert res.is_ok()
    out = res.unwrap()
    assert out["final_view_stack"] == ["A"]
    assert out["peak_depth_metric"] == 2

def test_react_native_nav_limit_reached():
    en = OmniReactNativeNavigationEngine(1)
    actions = [{"type": "PUSH", "route": "A"}, {"type": "PUSH", "route": "B"}]
    assert not en.execute_navigation_stack_matrix(actions).is_ok()

def test_react_native_nav_invalid_action():
    en = OmniReactNativeNavigationEngine()
    actions = [{"type": "JUMP"}]
    assert not en.execute_navigation_stack_matrix(actions).is_ok()

def test_react_native_nav_empty():
    en = OmniReactNativeNavigationEngine()
    assert not en.execute_navigation_stack_matrix([]).is_ok()

# ---------------------------------------------------------
# ENGINE 9: OmniGolangGinRouterEngine
# ---------------------------------------------------------
def test_golang_gin_diagnostics():
    en = OmniGolangGinRouterEngine()
    assert en.diagnostics()["status"] == "operational"

def test_golang_gin_valid_match():
    en = OmniGolangGinRouterEngine(10)
    defs = ["/user", "/post"]
    reqs = ["/user", "/unknown"]
    res = en.map_string_routing_boundaries(defs, reqs)
    assert res.is_ok()
    out = res.unwrap()
    assert "/user" in out["successfully_matched_paths"]
    assert "/unknown" in out["unmatched_404_paths"]

def test_golang_gin_capacity_limit():
    en = OmniGolangGinRouterEngine(1)
    assert not en.map_string_routing_boundaries(["/a", "/b"], ["/a"]).is_ok()

def test_golang_gin_empty_requests():
    en = OmniGolangGinRouterEngine()
    assert not en.map_string_routing_boundaries(["/a"], []).is_ok()

def test_golang_gin_empty_definitions():
    en = OmniGolangGinRouterEngine()
    assert not en.map_string_routing_boundaries([], ["/a"]).is_ok()

# ---------------------------------------------------------
# ENGINE 10: OmniPythonFastapiDiEngine
# ---------------------------------------------------------
def test_python_fastapi_di_diagnostics():
    en = OmniPythonFastapiDiEngine()
    assert en.diagnostics()["status"] == "operational"

def test_python_fastapi_di_valid_resolution():
    en = OmniPythonFastapiDiEngine(5)
    di_map = {"DB": [], "Repo": ["DB"], "Service": ["Repo"]}
    res = en.execute_dependency_resolution_graph(di_map, "Service")
    assert res.is_ok()
    out = res.unwrap()
    # Post-order traversal resolution mapping natively check!
    assert out["resolution_instantiation_order"] == ["DB", "Repo", "Service"]
    assert out["graph_max_depth_reached"] == 3

def test_python_fastapi_di_depth_exceeded():
    en = OmniPythonFastapiDiEngine(2)
    di_map = {"A": [], "B": ["A"], "C": ["B"]}
    # C(1) -> B(2) -> A(3 > limit)
    assert not en.execute_dependency_resolution_graph(di_map, "C").is_ok()

def test_python_fastapi_di_target_not_found():
    en = OmniPythonFastapiDiEngine()
    assert not en.execute_dependency_resolution_graph({"A": []}, "Unknown").is_ok()

def test_python_fastapi_di_empty_map():
    en = OmniPythonFastapiDiEngine()
    assert not en.execute_dependency_resolution_graph({}, "A").is_ok()

