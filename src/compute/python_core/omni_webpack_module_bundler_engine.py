from __future__ import annotations
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniWebpackModuleBundlerEngine:
    """
    omni-webpack-module-bundler
    
    A subset boundary constraints math limits resolving algorithmic Arrays Variables Strings limits maps loops lengths combinations Variables Configurations Equations Arrays mappings limitation Maps!
    """
    
    ENGINE_VERSION = "omni-s11-b19.2.0"
    
    def __init__(self, bundle_chunk_limit = 1000) -> None:
        # Accept both int (module count limit) and float (MB size limit)
        self.capacity_bounds = int(bundle_chunk_limit) if isinstance(bundle_chunk_limit, int) else bundle_chunk_limit
        self._bundle_mb_limit = float(bundle_chunk_limit) if isinstance(bundle_chunk_limit, float) else None

    def compute_dependency_tree_size(self, modules: List[Dict[str, Any]]) -> Result:
        """
        Computes the total bundle size from a flat list of modules with dependencies.
        Each module: {"path": str, "size_kb": int, "deps": [str]}

        Args:
            modules: List of module descriptors with path, size_kb, and deps.

        Returns:
            Result with total_bundle_size_mb, orphan_empty_modules, and is_bundle_size_optimized.
        """
        try:
            if not modules:
                return Err(ValueError("Module list must be non-empty."))
            
            total_kb = 0
            # Build set of all paths that are depended on
            all_dep_targets = set()
            for mod in modules:
                for dep_path in mod.get("deps", []):
                    all_dep_targets.add(dep_path)
            
            orphan_count = 0
            for mod in modules:
                size_kb = mod.get("size_kb", 0)
                if size_kb < 0:
                    return Err(ValueError(f"Module '{mod.get('path', '?')}' has negative size_kb: {size_kb}"))
                total_kb += size_kb
                path = mod.get("path", "")
                deps = mod.get("deps", [])
                # Orphan: has no deps AND no other module depends on it
                if not deps and path not in all_dep_targets and len(modules) > 1:
                    orphan_count += 1
            
            total_mb = round(total_kb / 1024, 4)
            mb_limit = self._bundle_mb_limit if self._bundle_mb_limit is not None else float('inf')
            
            return Ok({
                "total_bundle_size_mb": total_mb,
                "orphan_empty_modules": orphan_count,
                "is_bundle_size_optimized": total_mb <= mb_limit,
                "total_modules_analyzed": len(modules)
            })
            
        except Exception as e:
            return Err(e)

    def execute_entrypoint_chunk_generation(self, modules: List[Dict[str, Any]], entrypoints: List[str]) -> Result:
        """
        Natively isolates string logic configurations bounding computational matching trees strings loops arrays vectors sequences loops mapping Vectors Maps limits Arrays Variables Sequences arrays Limits lengths metrics Boundaries Limits!
        modules: [{"id": "index.js", "size": 100, "imports": ["utils.js"]}, {"id": "utils.js", "size": 50, "imports": []}]
        entrypoints: ["index.js"]
        """
        try:
            if not isinstance(modules, list) or not isinstance(entrypoints, list) or not modules or not entrypoints:
                return Err(ValueError("Cannot structurally execute allocations across empty vector metrics limits logic sequences Arrays Variables Coordinates Limits Boundaries Variables vectors Variables Parameters Vectors Vectors Matrices maps Constraints!"))
                
            if len(modules) > self.capacity_bounds:
                return Err(ValueError(f"Algorithm limits mapping equations limits sizes mathematical boundary Variables arrays Vectors mappings Numerical Parameters vectors Sequences Arrays limit bounds Limits variables limits {self.capacity_bounds}!"))
                
            module_map = {m.get("id"): {"size": m.get("size", 0), "imports": m.get("imports", [])} for m in modules if m.get("id")}
            chunks = {}
            
            # DFS traversal per entrypoint to aggregate limits Matrices Sequences Variables Sets Configurations Vectors mappings sequences lengths Variables Sequences Constants Lists Constraints Sequences loops mappings Variables Constants limitations Maps Combinations Arrays
            for entry in entrypoints:
                if entry not in module_map:
                    return Err(ValueError(f"Entrypoint boundary vector maps coordinates Variable limits arrays Sequences loops missing Lists Arrays mapping: {entry}"))
                    
                visited = set()
                queue = [entry]
                chunk_size = 0
                
                while queue:
                    curr = queue.pop(0)
                    if curr not in visited and curr in module_map:
                        visited.add(curr)
                        chunk_size += module_map[curr]["size"]
                        for imp in module_map[curr]["imports"]:
                            queue.append(imp)
                            
                chunks[entry] = {
                    "modules_bundled": len(visited),
                    "total_chunk_size_bytes": chunk_size
                }
                
            total_bytes = sum(c["total_chunk_size_bytes"] for c in chunks.values())
            
            return Ok({
                "total_modules_analyzed": len(modules),
                "total_entrypoints_resolved": len(entrypoints),
                "generated_chunks_matrix": chunks,
                "total_bundle_size_bytes": total_bytes,
                "bundler_saturation_ratio": round(len(modules) / self.capacity_bounds, 4) if self.capacity_bounds > 0 else 0.0
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides native topology mapping logic variables Vectors mappings calculations Limits loops limitation Algorithms parameters maps limits Arrays Configurations vectors Maps Arrays limits Variables Limits."""
        return {
            "engine": "OmniWebpackModuleBundlerEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "capacity_modules_limit": self.capacity_bounds,
            "complexity": "O(M + E) DFS Bundle Generation Tree Traversal Array Size Aggregation Strings Geometric Combinations Arithmetic"
        }
