import torch
from contextlib import contextmanager

class ComposerTrainer:
    """
    OMNI Engine: MosaicML Composer core training loop abstraction.
    Demonstrates speedup integrations (e.g. gradient accumulation, precise casting).
    """
    def __init__(self, model, optimizer, dataloader, device='cuda'):
        self.model = model.to(device)
        self.optimizer = optimizer
        self.dataloader = dataloader
        self.device = device
        self.scaler = torch.cuda.amp.GradScaler()

    def fit(self, epochs: int):
        self.model.train()
        for epoch in range(epochs):
            for batch_idx, (inputs, targets) in enumerate(self.dataloader):
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                
                self.optimizer.zero_grad()
                
                # Automatic Mixed Precision
                with torch.cuda.amp.autocast():
                    outputs = self.model(inputs)
                    loss = torch.nn.functional.cross_entropy(outputs, targets)
                
                self.scaler.scale(loss).backward()
                self.scaler.step(self.optimizer)
                self.scaler.update()
