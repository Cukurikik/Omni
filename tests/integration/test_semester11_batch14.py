import pytest
from src.compute.python_core.omni_webpack_module_bundler_engine import OmniWebpackModuleBundlerEngine
from src.compute.python_core.omni_django_celery_beat_engine import OmniDjangoCeleryBeatEngine
from src.compute.python_core.omni_flask_sqlalchemy_engine import OmniFlaskSqlalchemyEngine
from src.compute.python_core.omni_vuex_state_management_engine import OmniVuexStateManagementEngine
from src.compute.python_core.omni_nginx_reverse_proxy_engine import OmniNginxReverseProxyEngine
from src.compute.python_core.omni_spring_security_jwt_engine import OmniSpringSecurityJwtEngine
from src.compute.python_core.omni_aws_lambda_serverless_engine import OmniAwsLambdaServerlessEngine
from src.compute.python_core.omni_docker_compose_override_engine import OmniDockerComposeOverrideEngine
from src.compute.python_core.omni_react_router_dom_engine import OmniReactRouterDomEngine
from src.compute.python_core.omni_pytorch_lightning_training_engine import OmniPytorchLightningTrainingEngine

# ---------------------------------------------------------
# ENGINE 1: OmniWebpackModuleBundlerEngine
# ---------------------------------------------------------
def test_webpack_bundler_diagnostics():
    en = OmniWebpackModuleBundlerEngine()
    assert en.diagnostics()["status"] == "operational"

def test_webpack_bundler_valid():
    en = OmniWebpackModuleBundlerEngine(10.0)
    mods = [{"path": "a.js", "size_kb": 1024, "deps": ["b.js"]}, {"path": "b.js", "size_kb": 2048, "deps": []}]
    res = en.compute_dependency_tree_size(mods)
    assert res.is_ok()
    out = res.unwrap()
    assert out["total_bundle_size_mb"] == 3.0 # 1 + 2
    assert out["orphan_empty_modules"] == 0

def test_webpack_bundler_exceeded():
    en = OmniWebpackModuleBundlerEngine(1.0)
    mods = [{"path": "a.js", "size_kb": 2048}]
    res = en.compute_dependency_tree_size(mods)
    assert res.is_ok()
    assert en.compute_dependency_tree_size(mods).unwrap()["is_bundle_size_optimized"] is False

def test_webpack_bundler_negative_size():
    en = OmniWebpackModuleBundlerEngine()
    assert not en.compute_dependency_tree_size([{"path": "x", "size_kb": -10}]).is_ok()

def test_webpack_bundler_empty():
    en = OmniWebpackModuleBundlerEngine()
    assert not en.compute_dependency_tree_size([]).is_ok()

# ---------------------------------------------------------
# ENGINE 2: OmniDjangoCeleryBeatEngine
# ---------------------------------------------------------
def test_celery_beat_diagnostics():
    en = OmniDjangoCeleryBeatEngine()
    assert en.diagnostics()["status"] == "operational"

def test_celery_beat_valid():
    en = OmniDjangoCeleryBeatEngine(10)
    tasks = [{"name": "t1", "interval_mins": 60, "duration_mins": 5}]
    res = en.validate_cron_schedule_overlap(tasks)
    assert res.is_ok()
    assert res.unwrap()["schedule_isValid"] is True

def test_celery_beat_overlap():
    en = OmniDjangoCeleryBeatEngine(10)
    tasks = [{"name": "t1", "interval_mins": 5, "duration_mins": 10}]
    res = en.validate_cron_schedule_overlap(tasks)
    assert res.is_ok()
    assert res.unwrap()["schedule_isValid"] is False

def test_celery_beat_negative_dur():
    en = OmniDjangoCeleryBeatEngine()
    assert not en.validate_cron_schedule_overlap([{"name": "t", "interval_mins": 10, "duration_mins": -1}]).is_ok()

def test_celery_beat_empty():
    en = OmniDjangoCeleryBeatEngine()
    assert not en.validate_cron_schedule_overlap([]).is_ok()

# ---------------------------------------------------------
# ENGINE 3: OmniFlaskSqlalchemyEngine
# ---------------------------------------------------------
def test_flask_sqlalchemy_diagnostics():
    en = OmniFlaskSqlalchemyEngine()
    assert en.diagnostics()["status"] == "operational"

def test_flask_sqlalchemy_valid():
    en = OmniFlaskSqlalchemyEngine(10)
    models = [{"table_name": "t1", "columns": 5, "indexes": 2}]
    res = en.execute_sql_schema_migration(models)
    assert res.is_ok()
    out = res.unwrap()
    assert out["total_columns_created"] == 5
    assert out["migration_complexity_score"] == 9 # 5 + 2*2

def test_flask_sqlalchemy_exceeded():
    en = OmniFlaskSqlalchemyEngine(1)
    models = [{"table_name": "t1", "columns": 2}, {"table_name": "t2", "columns": 2}]
    assert not en.execute_sql_schema_migration(models).is_ok()

def test_flask_sqlalchemy_missing_cols():
    en = OmniFlaskSqlalchemyEngine()
    assert not en.execute_sql_schema_migration([{"table_name": "t"}]).is_ok()

def test_flask_sqlalchemy_empty():
    en = OmniFlaskSqlalchemyEngine()
    assert not en.execute_sql_schema_migration([]).is_ok()

# ---------------------------------------------------------
# ENGINE 4: OmniVuexStateManagementEngine
# ---------------------------------------------------------
def test_vuex_state_diagnostics():
    en = OmniVuexStateManagementEngine()
    assert en.diagnostics()["status"] == "operational"

def test_vuex_state_valid():
    en = OmniVuexStateManagementEngine(10)
    state = {"count": 10}
    muts = [{"type": "INCREMENT", "payload": 5}, {"type": "DECREMENT", "payload": 2}]
    res = en.execute_state_mutation_trace(state, muts)
    assert res.is_ok()
    out = res.unwrap()
    assert out["final_state_snapshot_matrix"]["count"] == 13

def test_vuex_state_reset():
    en = OmniVuexStateManagementEngine(10)
    res = en.execute_state_mutation_trace({"count": 50}, [{"type": "RESET"}])
    assert res.unwrap()["final_state_snapshot_matrix"]["count"] == 0

def test_vuex_state_unsupported():
    en = OmniVuexStateManagementEngine(10)
    res = en.execute_state_mutation_trace({"count": 1}, [{"type": "UNKNOWN"}])
    assert res.unwrap()["unsupported_mutation_types"] == ["UNKNOWN"]
    assert res.unwrap()["final_state_snapshot_matrix"]["count"] == 1

def test_vuex_state_empty_muts():
    en = OmniVuexStateManagementEngine()
    res = en.execute_state_mutation_trace({"n": 1}, [])
    assert res.is_ok()
    assert res.unwrap()["final_state_snapshot_matrix"]["n"] == 1

# ---------------------------------------------------------
# ENGINE 5: OmniNginxReverseProxyEngine
# ---------------------------------------------------------
def test_nginx_proxy_diagnostics():
    en = OmniNginxReverseProxyEngine()
    assert en.diagnostics()["status"] == "operational"

def test_nginx_proxy_valid():
    en = OmniNginxReverseProxyEngine(10)
    routes = {"/api": "b1", "/img": "b2"}
    reqs = ["/api/v1", "/api/v2", "/img/1.png"]
    res = en.calculate_proxy_pass_distribution(routes, reqs)
    assert res.is_ok()
    out = res.unwrap()
    assert out["backend_distribution_matrix"]["b1"] == 2
    assert out["backend_distribution_matrix"]["b2"] == 1

def test_nginx_proxy_unrouted():
    en = OmniNginxReverseProxyEngine(10)
    res = en.calculate_proxy_pass_distribution({"/api": "b"}, ["/auth"])
    assert res.unwrap()["unrouted_404_errors"] == 1

def test_nginx_proxy_exceeded():
    en = OmniNginxReverseProxyEngine(1)
    assert not en.calculate_proxy_pass_distribution({"/api": "b"}, ["1", "2"]).is_ok()

def test_nginx_proxy_empty():
    en = OmniNginxReverseProxyEngine()
    assert not en.calculate_proxy_pass_distribution({}, ["a"]).is_ok()

# ---------------------------------------------------------
# ENGINE 6: OmniSpringSecurityJwtEngine
# ---------------------------------------------------------
def test_spring_jwt_diagnostics():
    en = OmniSpringSecurityJwtEngine()
    assert en.diagnostics()["status"] == "operational"

def test_spring_jwt_valid():
    en = OmniSpringSecurityJwtEngine(3600)
    claims = {"sub": "user", "exp": 2000, "roles": ["admin"]}
    res = en.parse_jwt_claims_mathematically(claims, 1000)
    assert res.is_ok()
    out = res.unwrap()
    assert out["is_token_structurally_valid"] is True
    assert "ADMIN" in out["extracted_roles_vector"]

def test_spring_jwt_expired():
    en = OmniSpringSecurityJwtEngine(3600)
    claims = {"sub": "user", "exp": 500}
    res = en.parse_jwt_claims_mathematically(claims, 1000)
    assert res.unwrap()["is_token_structurally_valid"] is False
    assert "TOKEN_EXPIRED_MATHEMATICALLY" in res.unwrap()["validation_failure_reasons"]

def test_spring_jwt_missing_sub():
    en = OmniSpringSecurityJwtEngine()
    claims = {"exp": 2000}
    res = en.parse_jwt_claims_mathematically(claims, 1000)
    assert "MISSING_SUBJECT_CLAIM" in res.unwrap()["validation_failure_reasons"]

def test_spring_jwt_empty():
    en = OmniSpringSecurityJwtEngine()
    assert not en.parse_jwt_claims_mathematically({}, 1000).is_ok()

# ---------------------------------------------------------
# ENGINE 7: OmniAwsLambdaServerlessEngine
# ---------------------------------------------------------
def test_aws_lambda_diagnostics():
    en = OmniAwsLambdaServerlessEngine()
    assert en.diagnostics()["status"] == "operational"

def test_aws_lambda_valid():
    en = OmniAwsLambdaServerlessEngine(3000)
    logs = [{"duration_ms": 200, "init_duration_ms": 100}]
    res = en.compute_serverless_cold_start_metric(logs)
    assert res.is_ok()
    out = res.unwrap()
    assert out["total_simulated_billed_duration_ms"] == 300
    assert out["cold_start_events_traced"] == 1

def test_aws_lambda_timeout():
    en = OmniAwsLambdaServerlessEngine(100)
    logs = [{"duration_ms": 50}, {"duration_ms": 100}] # cumulative > 100
    res = en.compute_serverless_cold_start_metric(logs)
    assert res.unwrap()["execution_timeouts_flagged"] == 1

def test_aws_lambda_missing_dur():
    en = OmniAwsLambdaServerlessEngine()
    assert not en.compute_serverless_cold_start_metric([{"init_duration_ms": 10}]).is_ok()

def test_aws_lambda_empty():
    en = OmniAwsLambdaServerlessEngine()
    assert not en.compute_serverless_cold_start_metric([]).is_ok()

# ---------------------------------------------------------
# ENGINE 8: OmniDockerComposeOverrideEngine
# ---------------------------------------------------------
def test_docker_compose_override_diagnostics():
    en = OmniDockerComposeOverrideEngine()
    assert en.diagnostics()["status"] == "operational"

def test_docker_compose_override_valid():
    en = OmniDockerComposeOverrideEngine(30)
    b = {"web": {"image": "old", "port": 80}}
    o = {"web": {"image": "new"}}
    res = en.execute_compose_yaml_merge_logic(b, o)
    assert res.is_ok()
    out = res.unwrap()
    assert out["conflicting_service_keys_resolved"] == 1
    assert out["total_services_merged_structurally"] == 1

def test_docker_compose_override_new_service():
    en = OmniDockerComposeOverrideEngine(30)
    b = {"web": {"image": "old"}}
    o = {"db": {"image": "pg"}}
    res = en.execute_compose_yaml_merge_logic(b, o)
    assert res.unwrap()["total_services_merged_structurally"] == 2

def test_docker_compose_override_exceeded():
    en = OmniDockerComposeOverrideEngine(1)
    assert not en.execute_compose_yaml_merge_logic({"s1":{}}, {"s2":{}}).is_ok()

def test_docker_compose_override_empty():
    en = OmniDockerComposeOverrideEngine()
    assert not en.execute_compose_yaml_merge_logic({}, {}).is_ok()

# ---------------------------------------------------------
# ENGINE 9: OmniReactRouterDomEngine
# ---------------------------------------------------------
def test_react_router_diagnostics():
    en = OmniReactRouterDomEngine()
    assert en.diagnostics()["status"] == "operational"

def test_react_router_valid():
    en = OmniReactRouterDomEngine(10)
    tree = [{"path": "/a", "children": [{"path": "/b"}]}]
    res = en.execute_path_hierarchy_matching(tree, "/a/b")
    assert res.is_ok()
    out = res.unwrap()
    assert out["was_route_matched_structurally"] is True
    assert out["matched_route_hierarchy"] == ["/a", "/b"]

def test_react_router_no_match():
    en = OmniReactRouterDomEngine(10)
    tree = [{"path": "/a"}]
    res = en.execute_path_hierarchy_matching(tree, "/x")
    assert res.unwrap()["was_route_matched_structurally"] is False

def test_react_router_exceeded_depth():
    en = OmniReactRouterDomEngine(0) # Max depth 0 means root only
    tree = [{"path": "/a", "children": [{"path": "/b"}]}]
    assert not en.execute_path_hierarchy_matching(tree, "/a/b").is_ok()

def test_react_router_empty():
    en = OmniReactRouterDomEngine()
    assert not en.execute_path_hierarchy_matching([], "/a").is_ok()

# ---------------------------------------------------------
# ENGINE 10: OmniPytorchLightningTrainingEngine
# ---------------------------------------------------------
def test_pytorch_lightning_diagnostics():
    en = OmniPytorchLightningTrainingEngine()
    assert en.diagnostics()["status"] == "operational"

def test_pytorch_lightning_valid():
    en = OmniPytorchLightningTrainingEngine(100)
    # patience = 1.
    epochs = [{"val_loss": 0.5}, {"val_loss": 0.4}, {"val_loss": 0.5}]
    res = en.calculate_training_loss_convergence(epochs, 1)
    assert res.is_ok()
    out = res.unwrap()
    assert out["best_validation_loss"] == 0.4
    assert out["early_stopping_triggered"] is True
    assert out["simulated_epochs_run"] == 3

def test_pytorch_lightning_no_stop():
    en = OmniPytorchLightningTrainingEngine(100)
    epochs = [{"val_loss": 0.5}, {"val_loss": 0.4}, {"val_loss": 0.3}]
    res = en.calculate_training_loss_convergence(epochs, 3)
    assert res.unwrap()["early_stopping_triggered"] is False
    assert res.unwrap()["simulated_epochs_run"] == 3

def test_pytorch_lightning_negative_patience():
    en = OmniPytorchLightningTrainingEngine()
    assert not en.calculate_training_loss_convergence([{"val_loss": 1.0}], -1).is_ok()

def test_pytorch_lightning_empty():
    en = OmniPytorchLightningTrainingEngine()
    assert not en.calculate_training_loss_convergence([], 1).is_ok()

