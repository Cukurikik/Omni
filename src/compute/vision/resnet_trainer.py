import torch
import torch.nn as nn
import torch.optim as optim
from typing import Tuple, Any

class OmniResult:
    def __init__(self, ok: Any = None, err: str = None):
        self.ok = ok
        self.err = err
    
    def is_ok(self) -> bool:
        return self.err is None
        
    def unwrap(self) -> Any:
        if not self.is_ok():
            raise RuntimeError(f"Unwrap failed: {self.err}")
        return self.ok

class ResNetBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, stride: int = 1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = self.relu(out)
        return out

class ResNetTrainer:
    def __init__(self, num_classes: int, device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = torch.device(device)
        # Simplified ResNet structure for zero-mock architectural representation
        self.model = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            ResNetBlock(64, 64, stride=1),
            ResNetBlock(64, 128, stride=2),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(128, num_classes)
        ).to(self.device)
        
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)

    def train_step(self, images: torch.Tensor, labels: torch.Tensor) -> OmniResult:
        try:
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            self.model.train()
            self.optimizer.zero_grad()
            
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            
            loss.backward()
            self.optimizer.step()
            
            # Compute accuracy
            _, predicted = outputs.max(1)
            correct = predicted.eq(labels).sum().item()
            accuracy = correct / labels.size(0)
            
            return OmniResult(ok={"loss": loss.item(), "accuracy": accuracy})
        except Exception as e:
            return OmniResult(err=f"Training step failed: {str(e)}")
