"""OMNI Transformer Training — Package Init"""
from .trainer import OmniTrainer, TrainingConfig, CosineWarmupScheduler
from .data_pipeline import TextDataset, CausalLMDataset, DynamicPaddingCollator, create_dataloader
from .data_selection import DataWhisperer, DataSelectionConfig
from .gradient_checkpointing import CheckpointedSequential, enable_gradient_checkpointing, MemoryTracker
from .distributed import setup_distributed, cleanup_distributed, wrap_model_ddp
