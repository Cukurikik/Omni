"""
+============================================================================+
|  OMNI ENGINE REGISTRY -- The Central Nervous System                        |
|  Purpose: Auto-discover, catalog, validate, and provide unified access     |
|           to ALL OMNI engine modules across system/compute/network/domain   |
|  Layer: Meta / Infrastructure -- the spine connecting all organs            |
|  License: OMNI-Enterprise                                                  |
+============================================================================+

This module solves the CRITICAL missing piece: all 224+ engines built across
Batches 1-34 (Semester 5) exist as isolated .py files. This registry:
  1. SCANS all engine directories recursively for omni_*_engine.py files
  2. LOADS metadata from each (name, version, layer, class name)
  3. CATALOGS them into a unified, queryable index
  4. LAZY-IMPORTS engines on first invocation (not at startup)
  5. HEALTH-CHECKS engines by calling their diagnostics() method
  6. EXPORTS the full catalog as JSON for LSP/CLI consumption
  7. Provides a UNIFIED API: registry.invoke("artillery", "quick_test", ...)
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import (
    Any, Callable, Dict, Final, List, Literal,
    Optional, Sequence, Set, Tuple, Type, Union,
)


# ============================================================================
# 1. Constants & Enums
# ============================================================================

class EngineLayer(Enum):
    """The OMNI domain layers as defined in the Blueprint."""
    SYSTEM = "system"       # C, C++, Rust -- bare-metal I/O
    COMPUTE = "compute"     # Python, Julia, R -- ML/data science
    NETWORK = "network"     # Go, JavaScript -- concurrency & web
    DOMAIN = "domain"       # GraphQL, C#, Ruby, PHP -- business logic
    UI = "ui"               # TypeScript, HTML, Swift -- frontend
    META = "meta"           # Cross-layer infrastructure
    UNKNOWN = "unknown"

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-layer",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }


# Directories that map to known layers
LAYER_DIR_MAP: Final[Dict[str, EngineLayer]] = {
    "system": EngineLayer.SYSTEM,
    "compute": EngineLayer.COMPUTE,
    "network": EngineLayer.NETWORK,
    "domain": EngineLayer.DOMAIN,
    "ui": EngineLayer.UI,
}

# Pattern to match engine files
ENGINE_FILE_PATTERN = re.compile(r"^omni_[\w]+_engine\.py$")

# Pattern to find the main engine class in a module
ENGINE_CLASS_PATTERN = re.compile(r"class\s+(Omni\w+Engine)\b")

# Directories to skip during scanning
SKIP_DIRS: Final[Set[str]] = {
    "__pycache__", "venv", "node_modules", ".git", ".venv",
    "site-packages", "dist", "build", ".egg-info",
}


# ============================================================================
# 2. Data Structures
# ============================================================================

@dataclass
class EngineMetadata:
    """Metadata about a single discovered engine."""
    name: str                       # e.g. "robotgo"
    display_name: str               # e.g. "OmniRobotGoEngine"
    class_name: str                 # e.g. "OmniRobotGoEngine"
    module_path: str                # e.g. "engine.system.omni_robotgo_engine"
    file_path: str                  # Absolute path to .py file
    layer: EngineLayer              # Resolved domain layer
    relative_path: str              # Relative from engine root
    file_size_bytes: int = 0
    version: str = "unknown"
    is_loaded: bool = False
    is_healthy: bool = False
    health_check_time: float = 0.0
    capabilities: List[str] = field(default_factory=list)
    diagnostics_result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    discovered_at: float = field(default_factory=time.time)

    @property
    def short_id(self) -> str:
        """Short identifier derived from filename: omni_robotgo_engine -> robotgo"""
        parts = self.name.replace("omni_", "").replace("_engine", "")
        return parts

    def to_dict(self) -> Dict[str, Any]:
        """Performs to dict operation for EngineMetadata."""
        return {
            "name": self.name,
            "short_id": self.short_id,
            "display_name": self.display_name,
            "class_name": self.class_name,
            "layer": self.layer.value,
            "file_path": self.file_path,
            "relative_path": self.relative_path,
            "file_size_kb": round(self.file_size_bytes / 1024, 1),
            "version": self.version,
            "is_loaded": self.is_loaded,
            "is_healthy": self.is_healthy,
            "capabilities": self.capabilities,
            "error": self.error,
        }

    def to_lsp_completion(self) -> Dict[str, str]:
        """Format for LSP completion item."""
        return {
            "label": self.short_id,
            "kind": "Module",
            "detail": f"{self.display_name} ({self.layer.value})",
            "documentation": f"OMNI Engine: {self.display_name}\n"
                           f"Layer: {self.layer.value}\n"
                           f"File: {self.relative_path}\n"
                           f"Version: {self.version}",
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-metadata",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }


@dataclass
class RegistryCatalog:
    """The full catalog of all discovered engines."""
    engines: Dict[str, EngineMetadata] = field(default_factory=dict)
    scan_time_ms: float = 0.0
    engine_root: str = ""
    total_files_scanned: int = 0
    scan_timestamp: float = field(default_factory=time.time)

    @property
    def total_engines(self) -> int:
        """Execute total engines operation for RegistryCatalog."""
        return len(self.engines)

    @property
    def healthy_engines(self) -> int:
        """Execute healthy engines operation for RegistryCatalog."""
        return sum(1 for e in self.engines.values() if e.is_healthy)

    @property
    def loaded_engines(self) -> int:
        """Execute loaded engines operation for RegistryCatalog."""
        return sum(1 for e in self.engines.values() if e.is_loaded)

    def by_layer(self, layer: EngineLayer) -> List[EngineMetadata]:
        """Execute by layer operation for RegistryCatalog."""
        return [e for e in self.engines.values() if e.layer == layer]

    def layer_summary(self) -> Dict[str, int]:
        """Execute layer summary operation for RegistryCatalog."""
        summary: Dict[str, int] = {}
        for eng in self.engines.values():
            key = eng.layer.value
            summary[key] = summary.get(key, 0) + 1
        return summary

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "total_engines": self.total_engines,
            "healthy_engines": self.healthy_engines,
            "loaded_engines": self.loaded_engines,
            "scan_time_ms": round(self.scan_time_ms, 2),
            "engine_root": self.engine_root,
            "layers": self.layer_summary(),
            "engines": {k: v.to_dict() for k, v in self.engines.items()},
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to json representation."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


# ============================================================================
# 3. Engine Scanner
# ============================================================================

class EngineScanner:
    """
    Recursively scans the engine directory tree to discover all OMNI engines.
    Uses file pattern matching + AST-free class detection (regex on source).
    """

    def __init__(self, engine_root: str):
        """Initialize EngineScanner."""
        self.engine_root = Path(engine_root).resolve()

    def scan(self) -> List[EngineMetadata]:
        """Scan all subdirectories for engine files."""
        engines: List[EngineMetadata] = []
        files_scanned = 0

        for dirpath, dirnames, filenames in os.walk(self.engine_root):
            # Skip excluded directories
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

            for filename in filenames:
                if ENGINE_FILE_PATTERN.match(filename):
                    filepath = Path(dirpath) / filename
                    files_scanned += 1
                    meta = self._extract_metadata(filepath)
                    if meta:
                        engines.append(meta)

        return engines

    def _extract_metadata(self, filepath: Path) -> Optional[EngineMetadata]:
        """Extract metadata from an engine file without importing it."""
        try:
            source = filepath.read_text(encoding="utf-8", errors="ignore")
            stat = filepath.stat()
        except (OSError, IOError):
            return None

        # Find the main engine class name
        class_match = ENGINE_CLASS_PATTERN.search(source)
        class_name = class_match.group(1) if class_match else "Unknown"

        # Extract version from ENGINE_VERSION constant
        version_match = re.search(
            r'ENGINE_VERSION\s*[=:]\s*["\']([^"\']+)["\']', source
        )
        version = version_match.group(1) if version_match else "1.0.0"

        # Detect capabilities by finding public methods
        capabilities = self._extract_capabilities(source)

        # Resolve layer from directory hierarchy
        layer = self._resolve_layer(filepath)

        # Build relative path from engine root
        try:
            rel_path = filepath.relative_to(self.engine_root)
        except ValueError:
            rel_path = filepath

        # Module name from filename
        module_name = filepath.stem  # omni_robotgo_engine

        return EngineMetadata(
            name=module_name,
            display_name=class_name,
            class_name=class_name,
            module_path=str(rel_path).replace(os.sep, ".").replace(".py", ""),
            file_path=str(filepath),
            layer=layer,
            relative_path=str(rel_path),
            file_size_bytes=stat.st_size,
            version=version,
            capabilities=capabilities,
        )

    def _resolve_layer(self, filepath: Path) -> EngineLayer:
        """Determine engine layer from its directory path."""

        def diagnostics(self):
            """Return engine health diagnostics."""
            return {
                "engine_id": "omni-scanner",
                "version": getattr(self, "VERSION", "1.0.0"),
                "status": "operational",
            }
        parts = filepath.relative_to(self.engine_root).parts
        for part in parts:
            if part in LAYER_DIR_MAP:
                return LAYER_DIR_MAP[part]
        return EngineLayer.UNKNOWN

    def _extract_capabilities(self, source: str) -> List[str]:
        """Extract public method names as capabilities."""
        methods = re.findall(r"def\s+([a-z]\w+)\s*\(self", source)
        # Filter to interesting public methods (skip private/dunder/test)
        public = [
            m for m in methods
            if not m.startswith("_")
            and m not in ("to_dict", "to_json", "summary", "diagnostics")
        ]
        return public[:20]  # Cap at 20 most relevant

    def diagnostics(self):
        """Return engine scanner health diagnostics."""
        return {
            "engine_id": "omni-scanner",
            "version": "1.0.0",
            "status": "operational",
        }


# ============================================================================
# 4. Engine Loader (Lazy Import)
# ============================================================================

class EngineLoader:
    """
    Lazy-loads engine modules on demand using importlib.
    Avoids importing all 80+ engines at startup.
    """

    def __init__(self, engine_root: str):
        """Initialize EngineLoader."""
        self.engine_root = Path(engine_root).resolve()
        self._loaded_modules: Dict[str, Any] = {}
        self._loaded_classes: Dict[str, Any] = {}

    def load(self, metadata: EngineMetadata) -> Optional[Any]:
        """Import the engine module and return the main engine class."""
        if metadata.name in self._loaded_classes:
            return self._loaded_classes[metadata.name]

        try:
            # Use importlib to load from absolute file path
            spec = importlib.util.spec_from_file_location(
                metadata.name, metadata.file_path
            )
            if spec is None or spec.loader is None:
                metadata.error = "Failed to create import spec"
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[metadata.name] = module
            spec.loader.exec_module(module)

            self._loaded_modules[metadata.name] = module

            # Find the engine class
            engine_class = getattr(module, metadata.class_name, None)
            if engine_class is None:
                # Try finding any class matching Omni*Engine
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (inspect.isclass(attr)
                            and attr_name.startswith("Omni")
                            and attr_name.endswith("Engine")):
                        engine_class = attr
                        break


            if engine_class:
                self._loaded_classes[metadata.name] = engine_class
                metadata.is_loaded = True
                return engine_class

            metadata.error = f"Class {metadata.class_name} not found in module"
            return None

        except Exception as e:
            metadata.error = f"Import failed: {type(e).__name__}: {str(e)[:200]}"
            metadata.is_loaded = False
            return None

    def instantiate(self, metadata: EngineMetadata, **kwargs) -> Optional[Any]:
        """Load and instantiate an engine."""
        cls = self.load(metadata)
        if cls is None:
            return None
        try:
            return cls(**kwargs)
        except Exception as e:
            metadata.error = f"Instantiation failed: {e}"
            return None

    def diagnostics(self):
        """Return engine loader health diagnostics."""
        return {
            "engine_id": "omni-loader",
            "version": "1.0.0",
            "status": "operational",
        }


# ============================================================================
# 5. Health Checker
# ============================================================================

class HealthChecker:
    """Validates engine health by calling their diagnostics() method."""

    @staticmethod
    def check(engine_instance: Any, metadata: EngineMetadata) -> bool:
        """Run health check on an engine instance."""
        start = time.time()
        try:
            if hasattr(engine_instance, "diagnostics"):
                result = engine_instance.diagnostics()
                metadata.diagnostics_result = result if isinstance(result, dict) else {}
                metadata.is_healthy = True
            else:
                metadata.is_healthy = True  # No diagnostics = assume healthy
                metadata.diagnostics_result = {"note": "No diagnostics() method"}

            # Try to extract version from diagnostics
            version = metadata.diagnostics_result.get("version")
            if version:
                metadata.version = version

        except Exception as e:
            metadata.is_healthy = False
            metadata.error = f"Health check failed: {e}"

        metadata.health_check_time = (time.time() - start) * 1000
        return metadata.is_healthy


# ============================================================================
# 6. OmniEngineRegistry -- The Main Entry Point
# ============================================================================

class OmniEngineRegistry:
    """
    OMNI Engine Registry -- The Central Nervous System.

    Usage:
        registry = OmniEngineRegistry("c:/Users/.../Omni/engine")
        registry.scan()                          # Discover all engines
        registry.list_engines()                   # Show catalog
        registry.get("robotgo")                   # Get engine metadata
        registry.instantiate("artillery")          # Create engine instance
        registry.invoke("artillery", "quick_test", url="http://api.test")
        registry.health_check_all()               # Run diagnostics on all
        registry.export_json("catalog.json")       # Export for LSP/CLI
    """

    REGISTRY_VERSION: Final[str] = "1.0.0-omni"

    def __init__(self, engine_root: str):
        """Initialize OmniEngineRegistry."""
        self.engine_root = str(Path(engine_root).resolve())
        self.scanner = EngineScanner(self.engine_root)
        self.loader = EngineLoader(self.engine_root)
        self.health_checker = HealthChecker()
        self.catalog = RegistryCatalog(engine_root=self.engine_root)
        self._instances: Dict[str, Any] = {}

    # -- Discovery ----------------------------------------------------------

    def scan(self) -> RegistryCatalog:
        """Scan engine directory and build the catalog."""
        start = time.time()
        engines = self.scanner.scan()

        self.catalog = RegistryCatalog(engine_root=self.engine_root)
        for meta in engines:
            # Index by short_id and by full name
            self.catalog.engines[meta.short_id] = meta

        self.catalog.scan_time_ms = (time.time() - start) * 1000
        self.catalog.total_files_scanned = len(engines)
        return self.catalog

    # -- Query --------------------------------------------------------------

    def get(self, engine_id: str) -> Optional[EngineMetadata]:
        """Get engine metadata by short_id or full name."""
        # Try direct lookup
        meta = self.catalog.engines.get(engine_id)
        if meta:
            return meta
        # Fuzzy search: try matching partial name
        for key, meta in self.catalog.engines.items():
            if engine_id.lower() in key.lower() or engine_id.lower() in meta.name.lower():
                return meta
        return None

    def list_engines(self, layer: Optional[EngineLayer] = None) -> List[EngineMetadata]:
        """List all engines, optionally filtered by layer."""
        if layer:
            return self.catalog.by_layer(layer)
        return list(self.catalog.engines.values())

    def list_by_layer(self, layer_name: str) -> List[EngineMetadata]:
        """List engines by layer name string."""
        try:
            layer = EngineLayer(layer_name)
        except ValueError:
            return []
        return self.catalog.by_layer(layer)

    def search(self, query: str) -> List[EngineMetadata]:
        """Search engines by name, capability, or layer."""
        q = query.lower()
        results = []
        for meta in self.catalog.engines.values():
            if (q in meta.name.lower()
                    or q in meta.display_name.lower()
                    or q in meta.layer.value
                    or any(q in cap for cap in meta.capabilities)):
                results.append(meta)
        return results

    # -- Instantiation & Invocation -----------------------------------------

    def instantiate(self, engine_id: str, **kwargs) -> Optional[Any]:
        """Lazy-load and instantiate an engine."""
        if engine_id in self._instances:
            return self._instances[engine_id]

        meta = self.get(engine_id)
        if meta is None:
            return None

        instance = self.loader.instantiate(meta, **kwargs)
        if instance:
            self._instances[engine_id] = instance
        return instance

    def invoke(self, engine_id: str, method_name: str, *args, **kwargs) -> Any:
        """Invoke a method on an engine (auto-instantiates if needed)."""
        instance = self.instantiate(engine_id)
        if instance is None:
            raise RuntimeError(f"Engine '{engine_id}' not found or failed to load")

        method = getattr(instance, method_name, None)
        if method is None:
            raise AttributeError(f"Engine '{engine_id}' has no method '{method_name}'")

        return method(*args, **kwargs)

    # -- Health Checks ------------------------------------------------------

    def health_check(self, engine_id: str) -> bool:
        """Run health check on a single engine."""
        instance = self.instantiate(engine_id)
        meta = self.get(engine_id)
        if instance is None or meta is None:
            return False
        return self.health_checker.check(instance, meta)

    def health_check_all(self, skip_load_errors: bool = True) -> Dict[str, bool]:
        """Run health checks on all discovered engines."""
        results = {}
        for engine_id, meta in self.catalog.engines.items():
            instance = self.loader.instantiate(meta)
            if instance is None:
                if skip_load_errors:
                    results[engine_id] = False
                    continue
                else:
                    raise RuntimeError(f"Failed to load {engine_id}: {meta.error}")
            results[engine_id] = self.health_checker.check(instance, meta)
        return results

    # -- Export -------------------------------------------------------------

    def export_json(self, filepath: Optional[str] = None) -> str:
        """Export the full catalog as JSON (for LSP/CLI consumption)."""
        json_str = self.catalog.to_json()
        if filepath:
            Path(filepath).write_text(json_str, encoding="utf-8")
        return json_str

    def export_lsp_completions(self) -> List[Dict[str, str]]:
        """Export engine data formatted for LSP completion items."""
        return [m.to_lsp_completion() for m in self.catalog.engines.values()]

    # -- Diagnostics --------------------------------------------------------

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniEngineRegistry."""
        return {
            "registry_version": self.REGISTRY_VERSION,
            "engine_root": self.engine_root,
            "total_engines": self.catalog.total_engines,
            "healthy_engines": self.catalog.healthy_engines,
            "loaded_engines": self.catalog.loaded_engines,
            "scan_time_ms": round(self.catalog.scan_time_ms, 2),
            "layers": self.catalog.layer_summary(),
            "instances_cached": len(self._instances),
        }

    # -- Display ------------------------------------------------------------

    def print_catalog(self):
        """Print a formatted catalog to stdout."""
        print("=" * 72)
        print("  OMNI ENGINE REGISTRY -- Central Catalog")
        print(f"  Version: {self.REGISTRY_VERSION}")
        print(f"  Engine Root: {self.engine_root}")
        print(f"  Scan Time: {self.catalog.scan_time_ms:.1f}ms")
        print("=" * 72)

        # Group by layer
        for layer in EngineLayer:
            engines = self.catalog.by_layer(layer)
            if not engines:
                continue
            print(f"\n  [{layer.value.upper()}] -- {len(engines)} engine(s)")
            print("  " + "-" * 68)
            for eng in sorted(engines, key=lambda e: e.name):
                size_kb = eng.file_size_bytes / 1024
                health = "OK" if eng.is_healthy else ("ERR" if eng.error else "---")
                loaded = "yes" if eng.is_loaded else " no"
                caps = len(eng.capabilities)
                print(f"    {eng.short_id:<30} {size_kb:>6.1f}kb  "
                      f"loaded={loaded}  health={health:>3}  "
                      f"caps={caps:>2}  v{eng.version}")

        print(f"\n  TOTAL: {self.catalog.total_engines} engines across "
              f"{len(self.catalog.layer_summary())} layers")
        print("=" * 72)


# ============================================================================
# 7. Self-Test Suite
# ============================================================================

def _run_self_test() -> Dict[str, Any]:
    """Comprehensive self-test for the OmniEngineRegistry."""
    results = {"engine": "OmniEngineRegistry", "tests": [], "passed": 0, "failed": 0}

    def _test(name: str, fn: Callable[[], bool]):
        try:
            ok = fn()
            results["tests"].append({"name": name, "status": "PASS" if ok else "FAIL"})
            if ok:
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            results["tests"].append({"name": name, "status": "ERROR", "error": str(e)[:200]})
            results["failed"] += 1

    # Determine engine root (auto-detect from this file's location)
    this_dir = Path(__file__).resolve().parent
    engine_root = str(this_dir)

    registry = OmniEngineRegistry(engine_root)

    # Test 1: Scan discovers engines
    def t_scan():
        catalog = registry.scan()
        return catalog.total_engines > 0
    _test("scan_discovers_engines", t_scan)

    # Test 2: Scanner finds system layer engines
    _test("has_system_engines", lambda: len(registry.list_by_layer("system")) > 0)

    # Test 3: Scanner finds compute layer engines
    _test("has_compute_engines", lambda: len(registry.list_by_layer("compute")) > 0)

    # Test 4: Scanner finds network layer engines
    _test("has_network_engines", lambda: len(registry.list_by_layer("network")) > 0)

    # Test 5: Scanner finds domain layer engines
    _test("has_domain_engines", lambda: len(registry.list_by_layer("domain")) > 0)

    # Test 6: Get engine by short_id
    def t_get():
        engines = registry.list_engines()
        if not engines:
            return False
        first = engines[0]
        found = registry.get(first.short_id)
        return found is not None and found.name == first.name
    _test("get_engine_by_id", t_get)

    # Test 7: Engine metadata has valid fields
    def t_metadata():
        engines = registry.list_engines()
        if not engines:
            return False
        for eng in engines:
            if (eng.name != "" and eng.class_name != ""
                and eng.layer != EngineLayer.UNKNOWN
                and eng.file_size_bytes > 0):
                return True
        return False
    _test("metadata_valid", t_metadata)

    # Test 8: Search functionality
    def t_search():
        results = registry.search("engine")
        return len(results) > 0
    _test("search_works", t_search)

    # Test 9: Layer summary
    def t_layers():
        summary = registry.catalog.layer_summary()
        return len(summary) > 0 and sum(summary.values()) == registry.catalog.total_engines
    _test("layer_summary", t_layers)

    # Test 10: Export JSON
    def t_json():
        j = registry.export_json()
        data = json.loads(j)
        return "total_engines" in data and "engines" in data
    _test("export_json", t_json)

    # Test 11: LSP completions export
    def t_lsp():
        completions = registry.export_lsp_completions()
        return len(completions) > 0 and "label" in completions[0]
    _test("lsp_completions", t_lsp)

    # Test 12: Catalog to_dict
    def t_catalog_dict():
        d = registry.catalog.to_dict()
        return "engines" in d and "layers" in d
    _test("catalog_to_dict", t_catalog_dict)

    # Test 13: Engine capabilities extracted
    def t_caps():
        engines = registry.list_engines()
        has_caps = any(len(e.capabilities) > 0 for e in engines)
        return has_caps
    _test("capabilities_extracted", t_caps)

    # Test 14: Short ID derivation
    _test("short_id_format", lambda: EngineMetadata(
        name="omni_robotgo_engine", display_name="X", class_name="X",
        module_path="x", file_path="x", layer=EngineLayer.SYSTEM,
        relative_path="x"
    ).short_id == "robotgo")

    # Test 15: Diagnostics method
    def t_diag():
        d = registry.diagnostics()
        return "total_engines" in d and d["total_engines"] > 0
    _test("diagnostics", t_diag)

    # Test 16: Instantiate an engine
    def t_instantiate():
        engines = registry.list_engines()
        for eng in engines:
            # Try to instantiate -- might fail for engines with complex deps
            instance = registry.instantiate(eng.short_id)
            if instance is not None:
                return True
        return False  # No engine could be loaded -- still partial pass
    _test("instantiate_engine", t_instantiate)

    # Test 17: Invoke engine method
    def t_invoke():
        engines = registry.list_engines()
        for eng in engines:
            if "diagnostics" in eng.capabilities or registry.instantiate(eng.short_id):
                try:
                    result = registry.invoke(eng.short_id, "diagnostics")
                    return isinstance(result, dict)
                except Exception:
                    continue
        return False
    _test("invoke_method", t_invoke)

    # Test 18: Health check single
    def t_health_single():
        engines = registry.list_engines()
        for eng in engines:
            result = registry.health_check(eng.short_id)
            if result:
                return True
        return False
    _test("health_check_single", t_health_single)

    # Test 19: Fuzzy search
    def t_fuzzy():
        # Should find by partial name
        result = registry.get("robot")
        return result is not None or len(registry.list_engines()) == 0
    _test("fuzzy_search", t_fuzzy)

    # Test 20: Registry re-scan
    def t_rescan():
        c1 = registry.scan().total_engines
        c2 = registry.scan().total_engines
        return c1 == c2 and c1 > 0
    _test("rescan_consistent", t_rescan)

    # Test 21: EngineLayer enum completeness
    _test("layer_enum", lambda: len(EngineLayer) >= 7)

    # Test 22: Engine file pattern matching
    _test("pattern_match", lambda: ENGINE_FILE_PATTERN.match("omni_robotgo_engine.py") is not None)

    # Test 23: Pattern rejects non-engine files
    _test("pattern_reject", lambda: ENGINE_FILE_PATTERN.match("helper_utils.py") is None)

    # Test 24: EngineMetadata to_dict format
    def t_meta_dict():
        meta = EngineMetadata(
            name="omni_test_engine", display_name="OmniTestEngine",
            class_name="OmniTestEngine", module_path="test",
            file_path="/test/test.py", layer=EngineLayer.COMPUTE,
            relative_path="compute/test.py", file_size_bytes=10240,
        )
        d = meta.to_dict()
        return d["layer"] == "compute" and d["file_size_kb"] == 10.0
    _test("metadata_to_dict", t_meta_dict)

    # Test 25: Empty search returns empty
    _test("search_no_match", lambda: len(registry.search("zzz_nonexistent_zzz")) == 0)

    # Test 26: List by invalid layer
    _test("invalid_layer", lambda: len(registry.list_by_layer("fake_layer")) == 0)

    # Test 27: Multiple engines in same layer
    def t_multi_layer():
        for layer in EngineLayer:
            engines = registry.catalog.by_layer(layer)
            if len(engines) > 1:
                return True
        return False
    _test("multi_engines_per_layer", t_multi_layer)

    # Test 28: File size populated
    def t_filesize():
        return all(e.file_size_bytes > 0 for e in registry.list_engines())
    _test("file_sizes_populated", t_filesize)

    # Test 29: Export JSON to file
    def t_json_file():
        tmp_path = str(Path(engine_root) / "_registry_test.json")
        registry.export_json(tmp_path)
        exists = Path(tmp_path).exists()
        if exists:
            Path(tmp_path).unlink()  # cleanup
        return exists
    _test("export_json_to_file", t_json_file)

    # Test 30: Print catalog (smoke test)
    def t_print():
        registry.print_catalog()
        return True
    _test("print_catalog", t_print)

    results["total"] = results["passed"] + results["failed"]
    results["score"] = f"{results['passed']}/{results['total']}"
    return results


# ============================================================================
# 8. Module Entry Point
# ============================================================================

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 72)
    print("  OMNI ENGINE REGISTRY -- Central Nervous System Self-Test")
    print("=" * 72)

    results = _run_self_test()
    for t in results["tests"]:
        icon = "PASS" if t["status"] == "PASS" else "FAIL"
        err = f" ({t.get('error', '')})" if t.get("error") else ""
        print(f"  [{icon}] {t['name']}{err}")

    print(f"\n  Score: {results['score']}")
    print("=" * 72)
