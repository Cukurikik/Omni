import pytest
from src.compute.python_core.omni_wasm_edge_compute_engine import OmniWasmEdgeComputeEngine
from src.compute.python_core.omni_kubernetes_fleet_orchestrator_engine import OmniKubernetesFleetOrchestratorEngine
from src.compute.python_core.omni_three_js_voxel_renderer_engine import OmniThreeJSVoxelRendererEngine
from src.compute.python_core.omni_fastapi_data_router_engine import OmniFastAPIDataRouterEngine
from src.compute.python_core.omni_langchain_prompt_router_engine import OmniLangChainPromptRouterEngine
from src.compute.python_core.omni_webrtc_peer_to_peer_engine import OmniWebRTCPeerToPeerEngine
from src.compute.python_core.omni_nginx_reverse_proxy_routing_engine import OmniNginxReverseProxyRoutingEngine
from src.compute.python_core.omni_redis_lru_cache_eviction_engine import OmniRedisLRUCacheEvictionEngine
from src.compute.python_core.omni_rust_tokio_event_loop_engine import OmniRustTokioEventLoopEngine
from src.compute.python_core.omni_graphql_schema_resolver_engine import OmniGraphQLSchemaResolverEngine

# ---------------------------------------------------------
# ENGINE 1: OmniWasmEdgeComputeEngine
# ---------------------------------------------------------
def test_wasm_diagnostics():
    en = OmniWasmEdgeComputeEngine()
    assert en.diagnostics()["status"] == "operational"

def test_wasm_addition():
    en = OmniWasmEdgeComputeEngine()
    prog = ["PUSH 5", "PUSH 10", "ADD"]
    res = en.execute_ast_instruction_block(prog)
    assert res.is_ok()
    assert res.unwrap()["final_state"] == [15]

def test_wasm_empty():
    en = OmniWasmEdgeComputeEngine()
    assert not en.execute_ast_instruction_block([]).is_ok()

def test_wasm_stack_underflow():
    en = OmniWasmEdgeComputeEngine()
    prog = ["PUSH 5", "ADD"]
    assert not en.execute_ast_instruction_block(prog).is_ok()

def test_wasm_multiply_subtract():
    en = OmniWasmEdgeComputeEngine()
    prog = ["PUSH 10", "PUSH 5", "SUBTRACT", "PUSH 2", "MULTIPLY"]
    res = en.execute_ast_instruction_block(prog)
    # 10 5 SUB -> 10-5 = 5. Then 5 2 MULTIPLY -> 10.
    assert res.is_ok()
    assert res.unwrap()["final_state"] == [10]

# ---------------------------------------------------------
# ENGINE 2: OmniKubernetesFleetOrchestratorEngine
# ---------------------------------------------------------
def test_kube_diagnostics():
    en = OmniKubernetesFleetOrchestratorEngine([{"node_id": "n1", "cpu": 10.0, "ram": 20.0}])
    assert en.diagnostics()["status"] == "operational"

def test_kube_allocation_successful():
    en = OmniKubernetesFleetOrchestratorEngine([{"node_id": "n1", "cpu": 10.0, "ram": 20.0}])
    pods = [{"pod_id": "p1", "cpu": 5.0, "ram": 5.0}, {"pod_id": "p2", "cpu": 2.0, "ram": 2.0}]
    res = en.allocate_fleet_pods(pods)
    assert res.is_ok()
    data = res.unwrap()
    assert len(data["allocated"]) == 2
    assert len(data["pending"]) == 0
    assert data["utilization_metrics"]["total_free_cpu_left"] == 3.0

def test_kube_allocation_pending():
    en = OmniKubernetesFleetOrchestratorEngine([{"node_id": "n1", "cpu": 10.0, "ram": 10.0}])
    pods = [{"pod_id": "p1", "cpu": 8.0, "ram": 8.0}, {"pod_id": "p2", "cpu": 5.0, "ram": 5.0}]
    res = en.allocate_fleet_pods(pods)
    assert res.is_ok()
    data = res.unwrap()
    assert len(data["allocated"]) == 1
    assert len(data["pending"]) == 1

def test_kube_empty_pods():
    en = OmniKubernetesFleetOrchestratorEngine([{"node_id": "n1", "cpu": 10.0, "ram": 10.0}])
    assert not en.allocate_fleet_pods([]).is_ok()

def test_kube_best_fit():
    en = OmniKubernetesFleetOrchestratorEngine([
        {"node_id": "big_node", "cpu": 64.0, "ram": 128.0},
        {"node_id": "small_node", "cpu": 4.0, "ram": 8.0}
    ])
    pods = [{"pod_id": "p1", "cpu": 3.0, "ram": 6.0}]
    res = en.allocate_fleet_pods(pods)
    data = res.unwrap()
    assert data["allocated"][0]["node"] == "small_node"

# ---------------------------------------------------------
# ENGINE 3: OmniThreeJSVoxelRendererEngine
# ---------------------------------------------------------
def test_threejs_diagnostics():
    en = OmniThreeJSVoxelRendererEngine()
    assert en.diagnostics()["status"] == "operational"

def test_threejs_render_valid():
    en = OmniThreeJSVoxelRendererEngine(scale_ratio=2.0)
    res = en.transform_geometry_bounds([(10.0, 10.0, 10.0), (100.0, 100.0, 100.0)])
    assert res.is_ok()
    data = res.unwrap()
    assert data["rendered_buffer"][0] == (20.0, 20.0, 20.0)

def test_threejs_clipping():
    en = OmniThreeJSVoxelRendererEngine(scale_ratio=1.0)
    res = en.transform_geometry_bounds([(10.0, 10.0, 10.0), (2000.0, 0.0, 0.0)])
    assert res.is_ok()
    assert res.unwrap()["culled_amount"] == 1

def test_threejs_empty():
    en = OmniThreeJSVoxelRendererEngine()
    assert not en.transform_geometry_bounds([]).is_ok()

def test_threejs_negative_coord():
    en = OmniThreeJSVoxelRendererEngine(scale_ratio=0.5)
    res = en.transform_geometry_bounds([(-40.0, -100.0, 0.0)])
    assert res.is_ok()
    assert res.unwrap()["rendered_buffer"][0] == (-20.0, -50.0, 0.0)

# ---------------------------------------------------------
# ENGINE 4: OmniFastAPIDataRouterEngine
# ---------------------------------------------------------
def test_router_diagnostics():
    en = OmniFastAPIDataRouterEngine()
    assert en.diagnostics()["status"] == "operational"

def test_router_register_and_resolve():
    en = OmniFastAPIDataRouterEngine()
    en.register_endpoint_route("/users/create", "user_create")
    res = en.resolve_http_path("/users/create")
    assert res.is_ok()
    assert res.unwrap()["resolved_target"] == "user_create"

def test_router_dynamic_params():
    en = OmniFastAPIDataRouterEngine()
    en.register_endpoint_route("/users/{id}/profile", "user_profile")
    res = en.resolve_http_path("/users/abc-123/profile")
    assert res.is_ok()
    data = res.unwrap()
    assert data["resolved_target"] == "user_profile"
    assert data["dynamic_params"]["id"] == "abc-123"

def test_router_not_found():
    en = OmniFastAPIDataRouterEngine()
    en.register_endpoint_route("/users/", "users")
    assert not en.resolve_http_path("/admin/").is_ok()

def test_router_invalid_path():
    en = OmniFastAPIDataRouterEngine()
    assert not en.register_endpoint_route("users", "u").is_ok()
    assert not en.resolve_http_path("users").is_ok()

# ---------------------------------------------------------
# ENGINE 5: OmniLangChainPromptRouterEngine
# ---------------------------------------------------------
def test_prompt_diagnostics():
    en = OmniLangChainPromptRouterEngine()
    assert en.diagnostics()["status"] == "operational"

def test_prompt_perfect_match():
    en = OmniLangChainPromptRouterEngine()
    res = en.parse_and_route_parametric_template("Hello {name}, your id is {id}.", ["name", "id"])
    assert res.is_ok()
    assert res.unwrap()["template_validation_status"] == "perfect"

def test_prompt_missing_param_in_string():
    en = OmniLangChainPromptRouterEngine()
    res = en.parse_and_route_parametric_template("Hello {name}.", ["name", "id"])
    assert not res.is_ok()

def test_prompt_unexpected_param_in_string():
    en = OmniLangChainPromptRouterEngine()
    res = en.parse_and_route_parametric_template("Hello {name}, id {id}", ["name"])
    assert not res.is_ok()

def test_prompt_empty_params():
    en = OmniLangChainPromptRouterEngine()
    assert not en.parse_and_route_parametric_template("test", []).is_ok()

# ---------------------------------------------------------
# ENGINE 6: OmniWebRTCPeerToPeerEngine
# ---------------------------------------------------------
def test_webrtc_diagnostics():
    en = OmniWebRTCPeerToPeerEngine()
    assert en.diagnostics()["status"] == "operational"

def test_webrtc_host_to_host():
    en = OmniWebRTCPeerToPeerEngine(direct_weight=100)
    local = [{"ip": "local_ip", "type": "host"}, {"ip": "stun_ip", "type": "srflx"}]
    remote = [{"ip": "remote_ip", "type": "host"}, {"ip": "turn_ip", "type": "relay"}]
    res = en.compute_optimal_ice_route(local, remote)
    assert res.is_ok()
    data = res.unwrap()
    assert data["is_direct_subnet"] is True
    assert data["score"] == 200

def test_webrtc_invalid_type():
    en = OmniWebRTCPeerToPeerEngine()
    local = [{"ip": "test", "type": "unknown"}]
    remote = [{"ip": "r", "type": "host"}]
    assert not en.compute_optimal_ice_route(local, remote).is_ok()

def test_webrtc_empty():
    en = OmniWebRTCPeerToPeerEngine()
    assert not en.compute_optimal_ice_route([], []).is_ok()

def test_webrtc_fallback_to_relay():
    en = OmniWebRTCPeerToPeerEngine(turn_weight=5)
    local = [{"ip": "l1", "type": "relay"}]
    remote = [{"ip": "r1", "type": "relay"}]
    res = en.compute_optimal_ice_route(local, remote)
    assert res.is_ok()
    assert res.unwrap()["score"] == 10

# ---------------------------------------------------------
# ENGINE 7: OmniNginxReverseProxyRoutingEngine
# ---------------------------------------------------------
def test_nginx_diagnostics():
    en = OmniNginxReverseProxyRoutingEngine()
    assert en.diagnostics()["status"] == "operational"

def test_nginx_even_split():
    en = OmniNginxReverseProxyRoutingEngine()
    servers = [("s1", 10), ("s2", 10)]
    res = en.distribute_traffic_round_robin(servers, 100)
    assert res.is_ok()
    assert res.unwrap()["allocations"]["s1"] == 50

def test_nginx_weighted_split():
    en = OmniNginxReverseProxyRoutingEngine()
    servers = [("s1", 80), ("s2", 20)]
    res = en.distribute_traffic_round_robin(servers, 100)
    assert res.is_ok()
    assert res.unwrap()["allocations"]["s1"] == 80
    assert res.unwrap()["allocations"]["s2"] == 20

def test_nginx_invalid_weight():
    en = OmniNginxReverseProxyRoutingEngine()
    servers = [("s1", 0)]
    assert not en.distribute_traffic_round_robin(servers, 100).is_ok()

def test_nginx_empty_servers():
    en = OmniNginxReverseProxyRoutingEngine()
    assert not en.distribute_traffic_round_robin([], 100).is_ok()

# ---------------------------------------------------------
# ENGINE 8: OmniRedisLRUCacheEvictionEngine
# ---------------------------------------------------------
def test_redis_diagnostics():
    en = OmniRedisLRUCacheEvictionEngine(10)
    assert en.diagnostics()["status"] == "operational"

def test_redis_set_get():
    en = OmniRedisLRUCacheEvictionEngine(2)
    res = en.memory_block_command_stream(["SET A 1", "SET B 2", "GET A"])
    assert res.is_ok()
    data = res.unwrap()
    assert data["diagnostics"]["hits"] == 1
    assert data["cache_state"]["A"] == "1"

def test_redis_eviction():
    en = OmniRedisLRUCacheEvictionEngine(2)
    # A is oldest. Then B. Then we add C. A should be evicted.
    res = en.memory_block_command_stream(["SET A 1", "SET B 2", "SET C 3"])
    assert res.is_ok()
    data = res.unwrap()
    assert "A" not in data["cache_state"]
    assert "B" in data["cache_state"]
    assert "C" in data["cache_state"]
    assert data["total_evictions"] == 1

def test_redis_invalid_command():
    en = OmniRedisLRUCacheEvictionEngine(2)
    assert not en.memory_block_command_stream(["UNKNOWN A B"]).is_ok()

def test_redis_zero_capacity():
    en = OmniRedisLRUCacheEvictionEngine(0)
    assert not en.memory_block_command_stream(["SET A 1"]).is_ok()

# ---------------------------------------------------------
# ENGINE 9: OmniRustTokioEventLoopEngine
# ---------------------------------------------------------
def test_tokio_diagnostics():
    en = OmniRustTokioEventLoopEngine()
    assert en.diagnostics()["status"] == "operational"

def test_tokio_valid_polling():
    en = OmniRustTokioEventLoopEngine()
    futures = [{"id": "F1", "polls_required": 2}, {"id": "F2", "polls_required": 1}]
    res = en.execute_task_polling_topology(futures)
    assert res.is_ok()
    data = res.unwrap()
    # F1 -> 1 (Pending), F2 -> 0 (Ready), F1 -> 0 (Ready)
    assert data["resolution_metrics"] == ["F2", "F1"]
    assert data["cycles_exhausted"] == 3

def test_tokio_deadlock_limit():
    en = OmniRustTokioEventLoopEngine()
    futures = [{"id": "F1", "polls_required": 10005}] # Over the 10000 bound
    assert not en.execute_task_polling_topology(futures).is_ok()

def test_tokio_invalid_metric():
    en = OmniRustTokioEventLoopEngine()
    futures = [{"id": "F1", "polls_required": 0}]
    assert not en.execute_task_polling_topology(futures).is_ok()

def test_tokio_empty():
    en = OmniRustTokioEventLoopEngine()
    assert not en.execute_task_polling_topology([]).is_ok()

# ---------------------------------------------------------
# ENGINE 10: OmniGraphQLSchemaResolverEngine
# ---------------------------------------------------------
def test_graphql_diagnostics():
    en = OmniGraphQLSchemaResolverEngine()
    assert en.diagnostics()["status"] == "operational"

def test_graphql_valid_resolution():
    en = OmniGraphQLSchemaResolverEngine()
    query = "{ user { id name } }"
    payload = {"user": {"id": "1", "name": "Omni", "secret": "hidden"}}
    res = en.extract_nested_payload(query, payload)
    assert res.is_ok()
    data = res.unwrap()["data"]
    assert "secret" not in data["user"]
    assert data["user"]["id"] == "1"

def test_graphql_array_resolution():
    en = OmniGraphQLSchemaResolverEngine()
    query = "{ users { id } }"
    payload = {"users": [{"id": "1", "name": "A"}, {"id": "2"}]}
    res = en.extract_nested_payload(query, payload)
    assert res.is_ok()
    data = res.unwrap()["data"]
    assert data["users"][0] == {"id": "1"}

def test_graphql_invalid_syntax():
    en = OmniGraphQLSchemaResolverEngine()
    # Missing brackets
    query = "user id name"
    assert not en.extract_nested_payload(query, {"user": {}}).is_ok()

def test_graphql_empty():
    en = OmniGraphQLSchemaResolverEngine()
    assert not en.extract_nested_payload("", {}).is_ok()
