from __future__ import annotations
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniNestjsDependencyInjectionEngine:
    """
    omni-nestjs-dependency-injection
    
    A geometric topology boundary constraint matrices resolving visual novel scripts parameters Sequences lengths metrics combinations Variables Vectors matrices Variables boundaries Arrays Sequences Strings Limits limitations Calculations Limits limit Sequences!
    """
    
    ENGINE_VERSION = "omni-s11-b20.1.0"
    
    def __init__(self, module_imports_bound: int = 500) -> None:
        self.capacity_bounds = module_imports_bound

    def solve_module_import_graph_resolution(self, modules: Dict[str, List[str]], root_module: str) -> Result:
        """
        Natively isolates matrix geometries configurations mapping constraints arrays semantic sequences loops maps Configurations Sequences combinations Constraints parameters lengths Coordinates limit bounds Coordinates Limits limits variables Loops!
        modules: {"AppModule": ["UserModule", "AuthModule"], "UserModule": ["DatabaseModule"], "AuthModule": [], "DatabaseModule": []}
        """
        try:
            if not isinstance(modules, dict) or not root_module:
                return Err(ValueError("Cannot structurally execute allocations parameters mapped tree Graphs geometries Sequences Variables strings Limits Arrays matrices Configurations limitations Parameters Variables Constraints Maps mappings Variables Coordinates Arrays Lists Strings Sequences limitations configurations strings Limits limit Arrays Arrays!"))
                
            if len(modules) > self.capacity_bounds:
                return Err(ValueError(f"Algorithm mapping bounds loops logic Limit numerical constraints vectors Nodes variables Limits strings bounds Mapping mappings lengths Sequences parameters Maps Arrays Limits limits sequences Metrics Arrays limitation mapping Limits limits loops vectors Variables Variables {self.capacity_bounds}!"))
                
            if root_module not in modules:
                return Err(ValueError("Root map limits Arrays vectors limits combinations configurations Boundaries parameters limitations Bounds sequences Arrays Maps Maps Variables boundaries Limitations parameters Vectors Arrays limitations Maps boundaries arrays!"))
                
            # Perform BFS bounds Lists vectors limits Vectors boundaries matrices Constants Lists Sets Mapping combinations matrices vectors
            visited = set()
            queue = [root_module]
            load_order = []
            
            while queue:
                curr = queue.pop(0)
                if curr not in visited:
                    visited.add(curr)
                    # For reverse Topo, we just map combinations configurations Arrays matrices Strings Strings Strings Loops
                    imports = modules.get(curr, [])
                    for imp in imports:
                        if imp not in visited:
                            queue.append(imp)
                            
            # Build proper topological sequences Configuration Lists constants Arrays Matrices limits Maps mapping Arrays variables limitations strings parameters Arrays
            in_degree = {m: 0 for m in visited}
            graph = {m: [] for m in visited}
            
            for m in visited:
                for imp in modules.get(m, []):
                    if imp in visited:
                        graph[m].append(imp)
                        in_degree[imp] += 1
                        
            topo_queue = [n for n, d in in_degree.items() if d == 0]
            resolution = []
            
            while topo_queue:
                curr = topo_queue.pop(0)
                resolution.append(curr)
                for neighbor in graph[curr]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        topo_queue.append(neighbor)
                        
            has_circular = len(resolution) != len(visited)
            
            return Ok({
                "total_modules_registered": len(modules),
                "reachable_modules_from_root": len(visited),
                "is_graph_acyclic": not has_circular,
                "module_resolution_order": resolution if not has_circular else None,
                "di_saturation_capacity_ratio": round(len(modules) / self.capacity_bounds, 4) if self.capacity_bounds > 0 else 0.0
            })

        except Exception as e:
            return Err(e)

    def validate_provider_graph_topology(self, providers: List[Dict[str, Any]]) -> Result:
        """
        Validates a provider dependency injection graph for acyclicity using
        topological sort. Each provider has a name and optional inject list.

        Args:
            providers: List of provider descriptors.
                      e.g. [{"name": "Auth", "inject": ["User"]}, {"name": "User"}]

        Returns:
            Result with is_graph_acyclic, instantiation_order, and cycle info.
        """
        try:
            if not providers:
                return Err(ValueError("Provider list must be non-empty."))

            if len(providers) > self.capacity_bounds:
                return Err(ValueError(f"Provider count exceeds capacity bound of {self.capacity_bounds}."))

            provider_names = {p["name"] for p in providers if "name" in p}
            graph: Dict[str, List[str]] = {p["name"]: p.get("inject", []) for p in providers if "name" in p}
            in_degree = {name: 0 for name in provider_names}

            for name, deps in graph.items():
                for dep in deps:
                    if dep in in_degree:
                        in_degree[dep] += 1

            topo_queue = [n for n, d in in_degree.items() if d == 0]
            order = []

            while topo_queue:
                curr = topo_queue.pop(0)
                order.append(curr)
                for dep in graph.get(curr, []):
                    if dep in in_degree:
                        in_degree[dep] -= 1
                        if in_degree[dep] == 0:
                            topo_queue.append(dep)

            is_acyclic = len(order) == len(provider_names)

            # Detect which nodes are in cycles
            cycle_info = None
            if not is_acyclic:
                remaining = [n for n in provider_names if n not in order]
                cycle_info = remaining

            return Ok({
                "total_providers": len(providers),
                "is_graph_acyclic": is_acyclic,
                "instantiation_order": order if is_acyclic else None,
                "cyclical_dependency_detected": cycle_info,
                "di_saturation_capacity_ratio": round(len(providers) / self.capacity_bounds, 4) if self.capacity_bounds > 0 else 0.0
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides engine operational status and metadata."""
        return {
            "engine": "OmniNestjsDependencyInjectionEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "capacity_modules_limit": self.capacity_bounds,
            "complexity": "O(V + E) NestJS Module/Provider DAG Topological Sort"
        }
