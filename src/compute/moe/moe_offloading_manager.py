"""
moe_offloading_manager.py — System / Resource Management
Layer: Compute / System — Expert NVMe/CPU Offloading

Manages asynchronous offloading of inactive MoE experts to CPU memory
or NVMe storage. Prefetches experts back to GPU based on routing prediction
to enable training/inference of trillion-parameter MoE models on limited VRAM.
"""
import torch
import threading
import queue
import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class ExpertOffloadManager:
    """Manages moving experts between GPU, CPU, and Disk."""
    def __init__(self, num_experts: int, gpu_capacity: int, device: str = "cuda"):
        self.num_experts = num_experts
        self.gpu_capacity = gpu_capacity # Number of experts allowed on GPU
        self.device = torch.device(device)
        
        # State tracking
        self.on_gpu: Set[int] = set()
        self.on_cpu: Set[int] = set(range(num_experts))
        
        # Expert storage (mocked as simple dicts mapping id -> tensor tuple)
        self.cpu_storage: Dict[int, torch.Tensor] = {}
        self.gpu_storage: Dict[int, torch.Tensor] = {}
        
        # LRU tracking for eviction
        self.access_history: List[int] = []
        
        # Prefetch queue and worker thread
        self.prefetch_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._prefetch_worker, daemon=True)
        self.worker_thread.start()

    def register_expert_on_cpu(self, expert_id: int, w1: torch.Tensor, w2: torch.Tensor):
        """Initializes an expert in pinned CPU memory."""
        # Pin memory for fast async transfer to GPU
        self.cpu_storage[expert_id] = (w1.pin_memory(), w2.pin_memory())
        self.on_cpu.add(expert_id)

    def prefetch_experts(self, predicted_experts: List[int]):
        """Non-blocking request to move experts to GPU before they are needed."""
        for eid in predicted_experts:
            if eid not in self.on_gpu:
                self.prefetch_queue.put(eid)

    def _prefetch_worker(self):
        """Background thread handling async CPU -> GPU transfers."""
        # Create a separate CUDA stream for async transfers
        stream = torch.cuda.Stream(device=self.device) if self.device.type == "cuda" else None
        
        while True:
            expert_id = self.prefetch_queue.get()
            if expert_id is None: break # Shutdown signal
            
            if expert_id in self.on_gpu:
                self.prefetch_queue.task_done()
                continue
                
            self._ensure_capacity()
            
            w1_cpu, w2_cpu = self.cpu_storage[expert_id]
            
            if stream:
                with torch.cuda.stream(stream):
                    w1_gpu = w1_cpu.to(self.device, non_blocking=True)
                    w2_gpu = w2_cpu.to(self.device, non_blocking=True)
            else:
                w1_gpu = w1_cpu.to(self.device)
                w2_gpu = w2_cpu.to(self.device)
                
            self.gpu_storage[expert_id] = (w1_gpu, w2_gpu)
            self.on_gpu.add(expert_id)
            
            self.prefetch_queue.task_done()

    def _ensure_capacity(self):
        """Evicts the least recently used expert if GPU is full."""
        if len(self.on_gpu) >= self.gpu_capacity:
            # Find LRU expert
            for eid in reversed(self.access_history):
                if eid in self.on_gpu:
                    self._evict_to_cpu(eid)
                    break

    def _evict_to_cpu(self, expert_id: int):
        """Move expert from GPU back to CPU (or simply delete if CPU holds master copy)."""
        if expert_id in self.gpu_storage:
            del self.gpu_storage[expert_id]
        self.on_gpu.remove(expert_id)
        if self.device.type == "cuda":
            torch.cuda.empty_cache() # Or rely on PyTorch allocator

    def get_expert(self, expert_id: int) -> tuple:
        """Blocking call to get expert weights on GPU."""
        # Update LRU
        if expert_id in self.access_history:
            self.access_history.remove(expert_id)
        self.access_history.insert(0, expert_id)

        if expert_id in self.on_gpu:
            return self.gpu_storage[expert_id]

        # Cache miss, block and load
        logger.debug(f"Cache miss for expert {expert_id}. Blocking load.")
        self._ensure_capacity()
        w1_cpu, w2_cpu = self.cpu_storage[expert_id]
        
        w1_gpu = w1_cpu.to(self.device)
        w2_gpu = w2_cpu.to(self.device)
        
        self.gpu_storage[expert_id] = (w1_gpu, w2_gpu)
        self.on_gpu.add(expert_id)
        
        return w1_gpu, w2_gpu
