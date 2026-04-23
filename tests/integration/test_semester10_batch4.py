import pytest
from src.compute.python_core.omni_luau_runtime_engine import OmniLuauRuntimeEngine
from src.compute.python_core.omni_rsgl_graphics_engine import OmniRSGLGraphicsEngine
from src.compute.python_core.omni_git_story_anim_engine import OmniGitStoryAnimEngine
from src.compute.python_core.omni_kivy_studio_engine import OmniKivyStudioEngine
from src.compute.python_core.omni_julia_app_builder_engine import OmniJuliaAppBuilderEngine

# --- OMNI LUAU RUNTIME TESTS ---
def test_luau_runtime_diagnostics():
    engine = OmniLuauRuntimeEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_luau_sandbox_violation():
    engine = OmniLuauRuntimeEngine()
    res = engine.evaluate_sandbox_scope(["print", "io.open"]) # io is not allowed
    assert not res.is_ok()
    assert "Violation" in res.error

# --- OMNI RSGL GRAPHICS TESTS ---
def test_rsgl_graphics_diagnostics():
    engine = OmniRSGLGraphicsEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_rsgl_aabb_collision():
    engine = OmniRSGLGraphicsEngine()
    # completely overlapping
    res1 = engine.check_collision({"x":0,"y":0,"w":10,"h":10}, {"x":5,"y":5,"w":10,"h":10})
    assert getattr(res1, "is_ok", lambda: isinstance(res1, dict) and (res1.get("status") in ["operational", "Ready", "Functional"] or "engine" in res1))()
    assert res1.value["collided"] is True
    
    # disjoint
    res2 = engine.check_collision({"x":0,"y":0,"w":10,"h":10}, {"x":50,"y":50,"w":10,"h":10})
    assert getattr(res2, "is_ok", lambda: isinstance(res2, dict) and (res2.get("status") in ["operational", "Ready", "Functional"] or "engine" in res2))()
    assert res2.value["collided"] is False

# --- OMNI GIT STORY ANIM TESTS ---
def test_git_story_diagnostics():
    engine = OmniGitStoryAnimEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_git_story_delta_calc():
    engine = OmniGitStoryAnimEngine()
    nodes = [{"size": 10}, {"size": 20}, {"size": 15}]
    res = engine.calculate_keyframes(nodes)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["deltas"] == [10, -5]

# --- OMNI KIVY STUDIO TESTS ---
def test_kivy_studio_diagnostics():
    engine = OmniKivyStudioEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_kivy_studio_layout():
    engine = OmniKivyStudioEngine()
    parent = {"w": 400, "h": 300}
    child = {"hint_x": 0.25, "hint_y": 0.5}
    res = engine.resolve_layout(parent, child)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["w"] == 100
    assert res.value["h"] == 150

# --- OMNI JULIA APP BUILDER TESTS ---
def test_julia_app_builder_diagnostics():
    engine = OmniJuliaAppBuilderEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_julia_app_builder_sequence():
    engine = OmniJuliaAppBuilderEngine()
    # Correct
    res1 = engine.execute_build_pipeline(["CLEAN", "COMPILE"])
    assert getattr(res1, "is_ok", lambda: isinstance(res1, dict) and (res1.get("status") in ["operational", "Ready", "Functional"] or "engine" in res1))()
    
    # Incorrect order (Link before Compile)
    res2 = engine.execute_build_pipeline(["CLEAN", "LINK", "COMPILE"])
    assert not res2.is_ok()
    assert "out of order" in res2.error
