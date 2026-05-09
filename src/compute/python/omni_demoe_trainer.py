import os
import time
import logging
from typing import Dict, Any, Optional

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.cuda.amp import GradScaler, autocast
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

# OMNI MOTHER: Production DeMoE Training Loop
# Advanced Mixture-of-Experts trainer for image deblurring
# Implements mixed precision, gradient clipping, DDP, and fault tolerance.

class OmniDeMoETrainer:
    def __init__(
        self, 
        model: nn.Module, 
        dataloader: DataLoader, 
        val_dataloader: Optional[DataLoader],
        learning_rate: float = 1e-4,
        weight_decay: float = 1e-4,
        checkpoint_dir: str = "/opt/omni/checkpoints/demoe",
        local_rank: int = -1,
        mixed_precision: bool = True
    ):
        self.local_rank = local_rank
        self.device = torch.device(f"cuda:{local_rank}" if local_rank != -1 else "cuda:0")
        
        self.model = model.to(self.device)
        if self.local_rank != -1:
            self.model = DDP(self.model, device_ids=[self.local_rank], output_device=self.local_rank, find_unused_parameters=True)
            
        self.dataloader = dataloader
        self.val_dataloader = val_dataloader
        self.checkpoint_dir = checkpoint_dir
        self.mixed_precision = mixed_precision
        
        self.optimizer = optim.AdamW(
            self.model.parameters(), 
            lr=learning_rate, 
            weight_decay=weight_decay,
            betas=(0.9, 0.999)
        )
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=100)
        self.scaler = GradScaler(enabled=self.mixed_precision)
        
        # Loss functions: L1 for sharp restoration, plus perceptual loss
        self.l1_loss = nn.L1Loss().to(self.device)
        
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger("OmniDeMoETrainer")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers and (self.local_rank == -1 or self.local_rank == 0):
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(ch)

    def train_epoch(self, epoch: int) -> float:
        self.model.train()
        total_loss = 0.0
        start_time = time.time()
        
        for batch_idx, (blurred_img, sharp_img) in enumerate(self.dataloader):
            blurred_img = blurred_img.to(self.device, non_blocking=True)
            sharp_img = sharp_img.to(self.device, non_blocking=True)
            
            self.optimizer.zero_grad(set_to_none=True)
            
            with autocast(enabled=self.mixed_precision):
                restored_img, load_balancing_loss = self.model(blurred_img)
                recon_loss = self.l1_loss(restored_img, sharp_img)
                loss = recon_loss + 0.01 * load_balancing_loss
                
            self.scaler.scale(loss).backward()
            
            # Gradient clipping to prevent exploding gradients in MoE routing
            self.scaler.unscale_(self.optimizer)
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.scaler.step(self.optimizer)
            self.scaler.update()
            
            total_loss += loss.item()
            
            if batch_idx % 50 == 0 and (self.local_rank == -1 or self.local_rank == 0):
                self.logger.info(
                    f"Epoch [{epoch}] Batch [{batch_idx}/{len(self.dataloader)}] "
                    f"Loss: {loss.item():.4f} (Recon: {recon_loss.item():.4f}, Bal: {load_balancing_loss.item():.4f})"
                )
                
        self.scheduler.step()
        
        epoch_duration = time.time() - start_time
        avg_loss = total_loss / len(self.dataloader)
        
        if self.local_rank == -1 or self.local_rank == 0:
            self.logger.info(f"Epoch [{epoch}] Completed in {epoch_duration:.2f}s | Avg Loss: {avg_loss:.4f}")
            self.save_checkpoint(epoch, avg_loss)
            
        return avg_loss

    def save_checkpoint(self, epoch: int, loss: float):
        checkpoint_path = os.path.join(self.checkpoint_dir, f"demoe_epoch_{epoch}.pt")
        
        state_dict = self.model.module.state_dict() if isinstance(self.model, DDP) else self.model.state_dict()
        
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': state_dict,
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'scaler_state_dict': self.scaler.state_dict(),
            'loss': loss,
        }
        
        torch.save(checkpoint, checkpoint_path)
        self.logger.info(f"Checkpoint saved to {checkpoint_path}")

    def load_checkpoint(self, checkpoint_path: str):
        if not os.path.exists(checkpoint_path):
            self.logger.warning(f"Checkpoint {checkpoint_path} not found. Starting from scratch.")
            return 0
            
        self.logger.info(f"Loading checkpoint from {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        if isinstance(self.model, DDP):
            self.model.module.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.model.load_state_dict(checkpoint['model_state_dict'])
            
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        if 'scaler_state_dict' in checkpoint:
            self.scaler.load_state_dict(checkpoint['scaler_state_dict'])
            
        self.logger.info(f"Resuming from epoch {checkpoint['epoch']} with loss {checkpoint['loss']:.4f}")
        return checkpoint['epoch']
