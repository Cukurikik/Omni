# OMNI MOTHER: PiKV Scheduler
# Manages continuous batching for MoE decoding

class OmniPiKVScheduler:
    def __init__(self, allocator, eviction_policy):
        self.allocator = allocator
        self.eviction_policy = eviction_policy
        self.waiting_queue = []
        self.running_queue = []

    def add_request(self, seq_id: str):
        self.waiting_queue.append(seq_id)

    def step(self):
        # Promote waiting to running if blocks available
        for seq_id in self.waiting_queue[:]:
            try:
                self.allocator.allocate_block(seq_id)
                self.waiting_queue.remove(seq_id)
                self.running_queue.append(seq_id)
            except MemoryError:
                # Need eviction
                target = self.eviction_policy.find_eviction_target()
                if target:
                    self.allocator.free_request(target)
                    self.running_queue.remove(target)
                    # Retry next tick
                break
