import os
import copy
import logging
from typing import Dict, Any, List

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

# OMNI MOTHER: Drop-Upcycling MoE Trainer (Production Grade)
# Implements the logic to take a dense model, drop specific layers,
# and upcycle it into a sparse Mixture of Experts (MoE) model.

class OmniDropUpcyclingTrainer:
    def __init__(self, dense_model: nn.Module, moe_model: nn.Module, dataloader: DataLoader, lr: float = 1e-4):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.dense_model = dense_model.to(self.device)
        self.moe_model = moe_model.to(self.device)
        self.dataloader = dataloader
        self.optimizer = optim.AdamW(self.moe_model.parameters(), lr=lr)
        self.criterion = nn.CrossEntropyLoss()
        
        self.logger = logging.getLogger("OmniDropUpcycling")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(ch)

    def upcycle_weights(self, layer_mapping: Dict[str, str], num_experts: int = 8, noise_std: float = 0.02):
        """
        Transfers weights from the dense model to the MoE model.
        For expert layers, duplicates the dense FF layer 'num_experts' times and adds symmetry-breaking noise.
        """
        self.logger.info(f"[OMNI UPCYCLE] Beginning weight transfer to {num_experts} experts...")
        
        dense_state = self.dense_model.state_dict()
        moe_state = self.moe_model.state_dict()
        
        for moe_key, dense_key in layer_mapping.items():
            if dense_key not in dense_state:
                self.logger.warning(f"Dense key {dense_key} not found in source model.")
                continue
                
            if moe_key not in moe_state:
                self.logger.warning(f"MoE key {moe_key} not found in target model.")
                continue
                
            source_tensor = dense_state[dense_key]
            target_tensor = moe_state[moe_key]
            
            # Check if this is an expert layer (assuming standard shape mismatch means it's stacked experts)
            if target_tensor.shape != source_tensor.shape:
                # E.g., target is [num_experts, out_dim, in_dim], source is [out_dim, in_dim]
                if len(target_tensor.shape) == len(source_tensor.shape) + 1 and target_tensor.shape[0] == num_experts:
                    self.logger.info(f"Upcycling dense layer {dense_key} into {num_experts} experts at {moe_key}")
                    # Broadcast/copy the dense weights across all experts
                    stacked_weights = source_tensor.unsqueeze(0).expand(num_experts, *source_tensor.shape).clone()
                    
                    # Add noise to break symmetry, crucial for MoE training
                    noise = torch.randn_like(stacked_weights) * noise_std
                    moe_state[moe_key].copy_(stacked_weights + noise)
                else:
                    self.logger.error(f"Shape mismatch for {moe_key}: target {target_tensor.shape}, source {source_tensor.shape}")
            else:
                # Direct copy for non-expert layers (attention, layernorm, etc)
                moe_state[moe_key].copy_(source_tensor)
                
        self.moe_model.load_state_dict(moe_state)
        self.logger.info("[OMNI UPCYCLE] Weight transfer complete.")

    def train_epoch(self, epoch: int) -> float:
        self.moe_model.train()
        total_loss = 0.0
        
        for batch_idx, (inputs, targets) in enumerate(self.dataloader):
            inputs, targets = inputs.to(self.device), targets.to(self.device)
            
            self.optimizer.zero_grad()
            
            # Forward pass (assuming the MoE returns output and a load balancing loss)
            # Safe checking for our custom tuple return
            model_out = self.moe_model(inputs)
            if isinstance(model_out, tuple):
                outputs, aux_loss = model_out
            else:
                outputs = model_out
                aux_loss = torch.tensor(0.0).to(self.device)
            
            main_loss = self.criterion(outputs, targets)
            
            # Hyperparameter 0.01 controls the strength of the load balancing penalty
            loss = main_loss + 0.01 * aux_loss 
            
            loss.backward()
            
            # Clip gradients to prevent instability during early MoE training
            torch.nn.utils.clip_grad_norm_(self.moe_model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            
            total_loss += loss.item()
            
            if batch_idx % 100 == 0:
                self.logger.info(f"Epoch: {epoch} | Batch: {batch_idx} | Main Loss: {main_loss.item():.4f} | Aux Loss: {aux_loss.item():.4f}")
                
        if len(self.dataloader) == 0:
            return 0.0
            
        return total_loss / len(self.dataloader)
