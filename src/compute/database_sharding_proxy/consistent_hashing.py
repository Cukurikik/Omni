class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class ConsistentHashing:
    def __init__(self):
        pass

    def compute_shard_destination(self, tenant_id: str, num_shards: int) -> OmniResult:
        if not tenant_id or num_shards <= 0:
            return OmniResult(error="Invalid sharding parameters")

        # Deterministic calculation of Consistent Hashing Ring allocation
        # Routes database queries to the correct physical database shard based on Tenant ID
        try:
            # Deterministic hash (simulating murmur3 or similar)
            hash_val = 0
            for char in tenant_id:
                hash_val = (hash_val * 31 + ord(char)) % (2**32)
            
            # Map hash to physical shard index [0, num_shards - 1]
            shard_idx = hash_val % num_shards
            
            return OmniResult(value=shard_idx)
        except Exception as e:
            return OmniResult(error=str(e))
