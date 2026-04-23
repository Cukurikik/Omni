from __future__ import annotations
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniRedisClusterShardingEngine:
    """
    omni-redis-cluster-sharding
    
    A production-grade CRC16 hash slot distribution engine implementing the
    Redis Cluster key-to-slot mapping algorithm. Uses a native CRC16-CCITT
    polynomial (0x1021) lookup table — the same algorithm used by Redis itself
    to assign keys to one of 16384 hash slots.
    """
    
    ENGINE_VERSION = "omni-s11-b15.2.0"
    
    # CRC16 CCITT lookup table — pre-computed for the polynomial 0x1021.
    # This is the exact table Redis uses in its cluster.c implementation.
    _CRC16_TAB = None  # Lazy-initialized
    
    def __init__(self, key_processing_bound: int = 5000) -> None:
        self.capacity_bounds = key_processing_bound
        self.hash_slots_total = 16384  # Standard Redis Cluster slot count
        if OmniRedisClusterShardingEngine._CRC16_TAB is None:
            OmniRedisClusterShardingEngine._CRC16_TAB = self._build_crc16_table()

    @staticmethod
    def _build_crc16_table() -> List[int]:
        """
        Builds the CRC16-CCITT lookup table with polynomial 0x1021.
        This is the standard table used by Redis Cluster for slot assignment.

        Returns:
            List of 256 pre-computed CRC16 values.
        """
        table = []
        for i in range(256):
            crc = i << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc = crc << 1
            table.append(crc & 0xFFFF)
        return table

    def _crc16_hash_slot(self, key: str) -> int:
        """
        Computes the CRC16 hash slot for a given key using the CCITT polynomial.
        Handles Redis hash tags: if the key contains `{...}`, only the content
        inside the first pair of braces is hashed — enabling key co-location.

        Args:
            key: The Redis key string.

        Returns:
            An integer slot number in the range [0, 16383].
        """
        # Handle Redis hash tags for forced co-location
        hash_input = key
        lbrace = key.find('{')
        if lbrace >= 0:
            rbrace = key.find('}', lbrace + 1)
            if rbrace > lbrace + 1:
                hash_input = key[lbrace + 1:rbrace]
        
        # CRC16-CCITT computation
        crc = 0
        tab = OmniRedisClusterShardingEngine._CRC16_TAB
        for ch in hash_input.encode('utf-8'):
            crc = ((crc << 8) & 0xFFFF) ^ tab[((crc >> 8) ^ ch) & 0xFF]
        
        return crc % self.hash_slots_total

    def calculate_crc16_hash_slot_distribution(self, keys: List[str], cluster_nodes: int) -> Result:
        """
        Computes the CRC16 hash slot for each key and maps it to a cluster node.
        Uses the production Redis CRC16-CCITT algorithm for slot assignment.

        Args:
            keys: List of Redis key strings.
            cluster_nodes: Number of nodes in the cluster.

        Returns:
            Result containing slot assignments, node distribution, and metrics.
        """
        try:
            if not keys or cluster_nodes <= 0:
                return Err(ValueError("Keys must be non-empty and cluster_nodes must be positive."))
                
            if len(keys) > self.capacity_bounds:
                return Err(ValueError(f"Key count exceeds capacity bound of {self.capacity_bounds}."))
                
            slot_assignments = {}
            node_distribution = {n: 0 for n in range(cluster_nodes)}
            
            # Slots per node — even distribution across the hash ring
            slots_per_node = self.hash_slots_total // cluster_nodes
            
            for k in keys:
                slot = self._crc16_hash_slot(k)
                slot_assignments[k] = slot
                
                # Map slot to owning node via integer division
                target_node = min(slot // slots_per_node, cluster_nodes - 1)
                node_distribution[target_node] += 1
                
            return Ok({
                "keys_processed": len(keys),
                "cluster_shards_available": cluster_nodes,
                "calculated_key_slot_matrix": slot_assignments,
                "cluster_shard_hit_distribution": node_distribution,
                "key_saturation_ratio": round(len(keys) / self.capacity_bounds, 4)
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides engine operational status and metadata."""
        return {
            "engine": "OmniRedisClusterShardingEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "capacity_key_routing_bound": self.capacity_bounds,
            "complexity": "O(N) CRC16-CCITT Hash Slot Distribution Routing"
        }
