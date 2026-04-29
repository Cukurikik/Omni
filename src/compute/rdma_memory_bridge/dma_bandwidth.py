class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class DmaBandwidth:
    def __init__(self):
        pass

    def compute_rdma_throughput(self, message_size_bytes: int, latency_microseconds: float) -> OmniResult:
        if message_size_bytes <= 0 or latency_microseconds <= 0:
            return OmniResult(error="Invalid RDMA metrics")

        # Deterministic calculation of Remote Direct Memory Access (RDMA) throughput
        # Crucial for Infiniband network calculations when training massive LLMs across multiple server nodes
        try:
            # Throughput = Bytes / Time
            bytes_per_sec = message_size_bytes / (latency_microseconds * 1e-6)
            
            # Convert to Gigabits per second (Gbps) for standard networking metrics
            gbps = (bytes_per_sec * 8.0) / 1e9
            
            return OmniResult(value=gbps)
        except Exception as e:
            return OmniResult(error=str(e))
