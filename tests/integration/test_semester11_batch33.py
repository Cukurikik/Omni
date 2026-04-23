import pytest
from src.compute.python_core.omni_electron_builder_engine import OmniElectronBuilderEngine
from src.compute.python_core.omni_fast_api_router_engine import OmniFastApiRouterEngine
from src.compute.python_core.omni_rust_wasm_bindgen_engine import OmniRustWasmBindgenEngine
from src.compute.python_core.omni_celery_worker_engine import OmniCeleryWorkerEngine
from src.compute.python_core.omni_nginx_reverse_proxy_engine import OmniNginxReverseProxyEngine
from src.compute.python_core.omni_prisma_orm_engine import OmniPrismaOrmEngine
from src.compute.python_core.omni_socket_io_emitter_engine import OmniSocketIoEmitterEngine
from src.compute.python_core.omni_webpack_bundler_engine import OmniWebpackBundlerEngine
from src.compute.python_core.omni_flutter_widget_tree_engine import OmniFlutterWidgetTreeEngine
from src.compute.python_core.omni_ansible_playbook_engine import OmniAnsiblePlaybookEngine

class TestSemester11Batch33:
    
    # --- OmniElectronBuilderEngine ---
    def test_electron_register(self):
        engine = OmniElectronBuilderEngine()
        assert engine.register_package("app1", 100).is_ok()
        assert not engine.register_package("app1", 50).is_ok()
        assert not engine.register_package("app2", 0).is_ok()

    def test_electron_targets(self):
        engine = OmniElectronBuilderEngine()
        engine.register_package("app1", 100)
        assert engine.add_build_target("app1", "win32", "x64").is_ok()
        assert not engine.add_build_target("app1", "win32", "bad").is_ok()

    def test_electron_simulate(self):
        engine = OmniElectronBuilderEngine()
        engine.register_package("app1", 100)
        engine.add_build_target("app1", "win32", "x64")
        engine.add_build_target("app1", "linux", "arm64") 
        # win32_x64 -> 100 * 1.2 = 120
        # linux_arm64 -> 100 * 0.9 * 0.85 = 76.5 -> 76
        res = engine.simulate_build_size("app1").unwrap()
        assert res == 196

    def test_electron_empty_targets(self):
        engine = OmniElectronBuilderEngine()
        engine.register_package("app1", 100)
        assert not engine.simulate_build_size("app1").is_ok()

    def test_electron_missing_pkg(self):
        engine = OmniElectronBuilderEngine()
        assert not engine.simulate_build_size("ghost").is_ok()

    # --- OmniFastApiRouterEngine ---
    def test_fastapi_add_route(self):
        engine = OmniFastApiRouterEngine()
        assert engine.add_route("/api/v1/users", "GET", "get_users").is_ok()
        assert not engine.add_route("api", "GET", "get_users").is_ok()
        assert not engine.add_route("/api", "PATCH", "patch").is_ok()
        
    def test_fastapi_collision(self):
        engine = OmniFastApiRouterEngine()
        engine.add_route("/api", "GET", "f1")
        assert not engine.add_route("/api", "GET", "f2").is_ok()

    def test_fastapi_resolve_exact(self):
        engine = OmniFastApiRouterEngine()
        engine.add_route("/api/v1", "GET", "v1")
        engine.add_route("/api/v1", "POST", "create")
        assert engine.resolve_topology("/api/v1", "POST").unwrap() == "create"

    def test_fastapi_resolve_wildcard(self):
        engine = OmniFastApiRouterEngine()
        engine.add_route("/api/users/{id}", "GET", "get_user_by_id")
        assert engine.resolve_topology("/api/users/123", "GET").unwrap() == "get_user_by_id"
        
    def test_fastapi_complexity(self):
        engine = OmniFastApiRouterEngine()
        engine.add_route("/api", "GET", "1")
        engine.add_route("/api", "POST", "2")
        engine.add_route("/api/v2", "GET", "3")
        assert engine.compute_router_complexity().unwrap() == 1.5

    # --- OmniRustWasmBindgenEngine ---
    def test_wasm_alloc(self):
        engine = OmniRustWasmBindgenEngine(1)
        assert engine.allocate(100).unwrap() == 0
        assert engine.allocate(200).unwrap() == 100

    def test_wasm_out_of_mem(self):
        engine = OmniRustWasmBindgenEngine(1) # 65536
        assert engine.allocate(65000).is_ok()
        assert not engine.allocate(1000).is_ok()

    def test_wasm_strings(self):
        engine = OmniRustWasmBindgenEngine(1)
        ptr = engine.write_string_to_memory("hello world").unwrap()
        assert engine.read_string_from_memory(ptr, 11).is_ok()
        assert not engine.read_string_from_memory(ptr, 12).is_ok() # overflow read

    def test_wasm_str_empty(self):
        engine = OmniRustWasmBindgenEngine(1)
        assert not engine.allocate(0).is_ok()

    def test_wasm_fragmentation(self):
        engine = OmniRustWasmBindgenEngine(1)
        engine.allocate(6553)
        # 6553 / 65536 ~ 0.09999
        ratio = engine.get_fragmentation_ratio().unwrap()
        assert round(ratio, 4) == 0.1000

    # --- OmniCeleryWorkerEngine ---
    def test_celery_submit(self):
        engine = OmniCeleryWorkerEngine(2)
        assert engine.submit_task("t1", 10).is_ok()
        assert not engine.submit_task("t1", 10).is_ok()
        
    def test_celery_topological_sort(self):
        engine = OmniCeleryWorkerEngine(2)
        engine.submit_task("t3", 10, ["t1", "t2"])
        engine.submit_task("t1", 10)
        engine.submit_task("t2", 10, ["t1"])
        
        sort = engine.compute_topological_sort().unwrap()
        assert sort == ["t1", "t2", "t3"]

    def test_celery_deadlock(self):
        engine = OmniCeleryWorkerEngine(2)
        engine.submit_task("t1", 10, ["t2"])
        engine.submit_task("t2", 10, ["t1"])
        assert not engine.compute_topological_sort().is_ok()

    def test_celery_batch_exec(self):
        engine = OmniCeleryWorkerEngine(2)
        engine.submit_task("t1", 10)
        engine.submit_task("t2", 10)
        engine.submit_task("t3", 10, ["t1"])
        
        res = engine.execute_optimal_batch().unwrap()
        assert res == 2 # t1, t2 executed

    def test_celery_missing_dep(self):
        engine = OmniCeleryWorkerEngine(2)
        engine.submit_task("t1", 10, ["t2"])
        assert not engine.compute_topological_sort().is_ok()

    # --- OmniNginxReverseProxyEngine ---
    def test_nginx_add(self):
        engine = OmniNginxReverseProxyEngine(5)
        assert engine.add_upstream_server("10.0.0.1:80").is_ok()
        assert not engine.add_upstream_server("bad_ip_format").is_ok()

    def test_nginx_ring_eval(self):
        engine = OmniNginxReverseProxyEngine(5)
        engine.add_upstream_server("1.1.1.1:80")
        engine.add_upstream_server("2.2.2.2:80")
        target = engine.dispatch_request("192.168.0.1").unwrap()
        assert target in ["1.1.1.1:80", "2.2.2.2:80"]

    def test_nginx_removal(self):
        engine = OmniNginxReverseProxyEngine(5)
        engine.add_upstream_server("1.1.1.1:80")
        engine.remove_upstream_server("1.1.1.1:80")
        assert not engine.dispatch_request("1.1.1.1").is_ok()

    def test_nginx_empty_dispatch(self):
        engine = OmniNginxReverseProxyEngine(5)
        assert not engine.dispatch_request("ip").is_ok()

    def test_nginx_bad_remove(self):
        engine = OmniNginxReverseProxyEngine(5)
        engine.add_upstream_server("1.1.1.1:80")
        assert not engine.remove_upstream_server("2.2.2.2:80").is_ok()

    # --- OmniPrismaOrmEngine ---
    def test_prisma_parse(self):
        engine = OmniPrismaOrmEngine()
        assert engine.parse_model("User", {"id": "Int", "name": "String", "posts": "Post[]"}).is_ok()
        assert not engine.parse_model("User", {"age": "Int"}).is_ok() # Duplicate
        
    def test_prisma_invalid_type(self):
        engine = OmniPrismaOrmEngine()
        assert not engine.parse_model("T", {"x": "alien"}).is_ok()

    def test_prisma_relations(self):
        engine = OmniPrismaOrmEngine()
        engine.parse_model("User", {"id": "Int", "post": "Post"})
        engine.parse_model("Post", {"id": "Int", "author": "User"})
        assert engine.validate_relations().unwrap() == 2

    def test_prisma_broken_relation(self):
        engine = OmniPrismaOrmEngine()
        engine.parse_model("User", {"id": "Int", "post": "P"})
        assert not engine.validate_relations().is_ok()

    def test_prisma_sql(self):
        engine = OmniPrismaOrmEngine()
        engine.parse_model("M", {"id": "Int", "opt": "String?"})
        sql = engine.generate_sql_stub("M").unwrap()
        assert "CREATE TABLE \"M\"" in sql
        assert "\"id\" INTEGER NOT NULL" in sql
        assert "\"opt\" TEXT" in sql

    # --- OmniSocketIoEmitterEngine ---
    def test_socket_connect(self):
        engine = OmniSocketIoEmitterEngine(10)
        assert engine.connect_client("c1").is_ok()
        assert not engine.connect_client("c1").is_ok()

    def test_socket_overload(self):
        engine = OmniSocketIoEmitterEngine(1)
        engine.connect_client("c1")
        assert not engine.connect_client("c2").is_ok()

    def test_socket_join(self):
        engine = OmniSocketIoEmitterEngine(10)
        engine.connect_client("c1")
        assert engine.join_room("c1", "room1").is_ok()

    def test_socket_measure(self):
        engine = OmniSocketIoEmitterEngine(10)
        engine.connect_client("c1")
        engine.connect_client("c2")
        engine.join_room("c1", "r1")
        engine.join_room("c2", "r1")
        
        assert engine.measure_fanout("r1", 500).unwrap() == 1000

    def test_socket_measure_empty(self):
        engine = OmniSocketIoEmitterEngine(10)
        engine.connect_client("c1")
        assert engine.measure_fanout("ghost", 100).unwrap() == 0

    # --- OmniWebpackBundlerEngine ---
    def test_webpack_register(self):
        engine = OmniWebpackBundlerEngine()
        assert engine.register_module("a", 100).is_ok()
        assert not engine.register_module("a", 100).is_ok()

    def test_webpack_bundle(self):
        engine = OmniWebpackBundlerEngine()
        engine.register_module("a", 10, ["b", "c"])
        engine.register_module("b", 20)
        engine.register_module("c", 30)
        res = engine.extract_bundle("a").unwrap()
        assert res["chunk"] == ["b", "c", "a"]
        assert res["volume"] == 60

    def test_webpack_cycle(self):
        engine = OmniWebpackBundlerEngine()
        engine.register_module("a", 10, ["b"])
        engine.register_module("b", 10, ["a"])
        assert not engine.extract_bundle("a").is_ok()

    def test_webpack_missing_import(self):
        engine = OmniWebpackBundlerEngine()
        engine.register_module("a", 10, ["d"])
        assert not engine.extract_bundle("a").is_ok()

    def test_webpack_invalid_size(self):
        engine = OmniWebpackBundlerEngine()
        assert not engine.register_module("a", -1).is_ok()

    # --- OmniFlutterWidgetTreeEngine ---
    def test_flutter_attach(self):
        engine = OmniFlutterWidgetTreeEngine()
        assert engine.attach_widget("w1", 10, 10).is_ok()

    def test_flutter_geom(self):
        engine = OmniFlutterWidgetTreeEngine()
        engine.attach_widget("r", 50, 50)
        engine.attach_widget("c", 10, 10, "r")
        assert engine.get_geometric_bounds("r").unwrap() == 2600

    def test_flutter_paint(self):
        engine = OmniFlutterWidgetTreeEngine()
        engine.attach_widget("r", 10, 10)
        engine.attach_widget("c", 10, 10, "r")
        
        engine.mark_needs_paint("c")
        assert engine.widget_tree["c"]["needs_paint"] == True
        assert engine.widget_tree["r"]["needs_paint"] == True

    def test_flutter_render(self):
        engine = OmniFlutterWidgetTreeEngine()
        engine.attach_widget("r", 10, 10)
        engine.mark_needs_paint("r")
        assert engine.trigger_frame_render().unwrap() == 1
        assert engine.paint_cycles == 1
        assert engine.trigger_frame_render().unwrap() == 0

    def test_flutter_bad_node(self):
        engine = OmniFlutterWidgetTreeEngine()
        assert not engine.attach_widget("a", 0, 10).is_ok()

    # --- OmniAnsiblePlaybookEngine ---
    def test_ansible_reg(self):
        engine = OmniAnsiblePlaybookEngine()
        assert engine.register_server("s1").is_ok()

    def test_ansible_playbook_exec(self):
        engine = OmniAnsiblePlaybookEngine()
        engine.register_server("s1")
        res = engine.execute_playbook("s1", [{"name": "pkg", "value": "installed"}]).unwrap()
        assert res["changed"] == 1
        
        res2 = engine.execute_playbook("s1", [{"name": "pkg", "value": "installed"}]).unwrap()
        assert res2["changed"] == 0
        assert res2["ok"] == 1

    def test_ansible_drift(self):
        engine = OmniAnsiblePlaybookEngine()
        engine.register_server("s1")
        engine.execute_playbook("s1", [{"name": "a", "value": "1"}])
        assert engine.verify_state_drift("s1", {"a": "1"}).unwrap() == 0
        assert engine.verify_state_drift("s1", {"a": "2"}).unwrap() == 1

    def test_ansible_drift_unmapped(self):
        engine = OmniAnsiblePlaybookEngine()
        engine.register_server("s1")
        engine.execute_playbook("s1", [{"name": "extra", "value": "1"}])
        assert engine.verify_state_drift("s1", {}).unwrap() == 1

    def test_ansible_bad_playbook(self):
        engine = OmniAnsiblePlaybookEngine()
        engine.register_server("s1")
        assert not engine.execute_playbook("s1", [{"bad": "format"}]).is_ok()
