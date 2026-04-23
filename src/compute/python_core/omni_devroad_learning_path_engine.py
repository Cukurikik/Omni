"""OmniDevroadLearningPathEngine — Developer Roadmap Path Optimizer.

Inspired by colomolo/devroad-data: a community-sourced collection
of organized developer learning resources structured as a technology
roadmap with dependencies between topics.

Algorithmic Primitive:
    Model a learning roadmap as a Directed Acyclic Graph (DAG) where
    nodes are topics and edges are prerequisites. Compute valid
    learning orders via topological sort, identify the critical
    (longest) path through the roadmap, and track learner progress
    to suggest the next actionable topics.
"""
from __future__ import annotations
from collections import deque
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniDevroadLearningPathEngine:
    """Production-grade developer roadmap path optimizer using DAG analysis."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniDevroadLearningPathEngine",
            "version": "1.0.0",
            "primitive": "dag_topological_learning_path_optimization",
            "monadic_enforcement": True,
            "source_repo": "colomolo/devroad-data",
        }

    @staticmethod
    def compute_learning_order(
        topics: list[str],
        prerequisites: list[tuple[str, str]],
    ) -> Result:
        """Compute a valid learning order via topological sort (Kahn's).

        Args:
            topics: List of topic names.
            prerequisites: List of (prerequisite, topic) tuples meaning
                           'prerequisite' must be learned before 'topic'.

        Returns:
            Result[list[str], Exception]: Topologically sorted topic list.
            Returns Err if a cycle is detected.
        """
        if not isinstance(topics, list) or len(topics) == 0:
            return Err(Exception("topics must be a non-empty list"))

        topic_set = set(topics)
        adj: dict[str, list[str]] = {t: [] for t in topics}
        in_degree: dict[str, int] = {t: 0 for t in topics}

        for prereq, topic in prerequisites:
            if prereq not in topic_set:
                return Err(Exception(f"Unknown prerequisite: '{prereq}'"))
            if topic not in topic_set:
                return Err(Exception(f"Unknown topic: '{topic}'"))
            adj[prereq].append(topic)
            in_degree[topic] += 1

        # Kahn's algorithm
        queue: deque[str] = deque(t for t in topics if in_degree[t] == 0)
        order: list[str] = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(topics):
            return Err(Exception("Cycle detected in prerequisite graph"))

        return Ok(order)

    @staticmethod
    def find_critical_path(
        topics: list[str],
        prerequisites: list[tuple[str, str]],
    ) -> Result:
        """Find the longest path through the learning DAG (critical path).

        Args:
            topics: List of topic names.
            prerequisites: List of (prerequisite, topic) tuples.

        Returns:
            Result[dict, Exception]: dict with 'critical_path' (list[str]),
            'length' (int).
        """
        order_result = OmniDevroadLearningPathEngine.compute_learning_order(
            topics, prerequisites
        )
        if not order_result.is_ok():
            return order_result

        order = order_result.unwrap()

        # Build adjacency
        adj: dict[str, list[str]] = {t: [] for t in topics}
        for prereq, topic in prerequisites:
            adj[prereq].append(topic)

        # Longest path via DP on topological order
        dist: dict[str, int] = {t: 0 for t in topics}
        parent: dict[str, str | None] = {t: None for t in topics}

        for node in order:
            for neighbor in adj[node]:
                if dist[node] + 1 > dist[neighbor]:
                    dist[neighbor] = dist[node] + 1
                    parent[neighbor] = node

        # Find the node with maximum distance
        end_node = max(dist, key=dist.get)  # type: ignore[arg-type]
        max_length = dist[end_node]

        # Reconstruct path
        path: list[str] = []
        current: str | None = end_node
        while current is not None:
            path.append(current)
            current = parent[current]
        path.reverse()

        return Ok({
            "critical_path": path,
            "length": max_length,
        })

    @staticmethod
    def suggest_next_topics(
        topics: list[str],
        prerequisites: list[tuple[str, str]],
        completed: list[str],
    ) -> Result:
        """Suggest the next learnable topics based on completed ones.

        A topic is 'actionable' if all its prerequisites are completed
        and it is not yet completed itself.

        Args:
            topics: List of all topic names.
            prerequisites: List of (prerequisite, topic) tuples.
            completed: List of already completed topic names.

        Returns:
            Result[list[str], Exception]: Sorted list of actionable topics.
        """
        if not isinstance(topics, list):
            return Err(Exception("topics must be a list"))

        topic_set = set(topics)
        completed_set = set(completed)

        # Build prerequisite map: topic -> set of prereqs
        prereq_map: dict[str, set[str]] = {t: set() for t in topics}
        for prereq, topic in prerequisites:
            if topic in topic_set and prereq in topic_set:
                prereq_map[topic].add(prereq)

        actionable: list[str] = []
        for topic in topics:
            if topic in completed_set:
                continue
            if prereq_map[topic].issubset(completed_set):
                actionable.append(topic)

        return Ok(sorted(actionable))
