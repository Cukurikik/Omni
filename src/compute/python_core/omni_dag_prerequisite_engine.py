"""OmniDagPrerequisiteEngine for ordering directed acyclic prerequisites."""
from typing import Dict, Any, List, Set
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniDagPrerequisiteEngine(OmniBaseEngine):
    """Production-grade Omni Dag Prerequisite Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def resolve_order(self, courses: List[str], prerequisites: List[tuple]) -> Result[Dict[str, Any], str]:
        """
        Uses Kahn's Algorithm to topologically sort courses based on prerequisites.
        Prerequisite tuples are (prereq, course).
        Returns failure if a cycle is detected.
        """
        try:
            in_degree: Dict[str, int] = {c: 0 for c in courses}
            adj_list: Dict[str, List[str]] = {c: [] for c in courses}

            # Build graph
            for prereq, course in prerequisites:
                if prereq not in in_degree or course not in in_degree:
                    return Result.fail(f"Unknown course in prereqs: {prereq} -> {course}")
                adj_list[prereq].append(course)
                in_degree[course] += 1

            # Deterministic queue extraction (sorting degree 0 nodes)
            queue = [c for c in courses if in_degree[c] == 0]
            queue.sort()
            
            resolved_order = []

            while queue:
                current = queue.pop(0)
                resolved_order.append(current)

                neighbors = sorted(adj_list[current])
                for neighbor in neighbors:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
                        queue.sort() # Ensure deterministic ordering of concurrent options

            if len(resolved_order) != len(courses):
                return Result.fail("Cycle detected: Prerequisites form a closed loop")

            return Result.ok({
                "resolved_order": resolved_order,
                "is_dag": True
            })
            
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniDagPrerequisiteEngine",
            "status": "operational",
            "algorithm": "Kahn's Topological Sort"
        }
