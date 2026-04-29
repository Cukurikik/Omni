import torch
import torch.nn as nn
from typing import Dict, Any, Tuple

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

class SimpleUNet(nn.Module):
    def __init__(self, sources: int = 4):
        super().__init__()
        self.sources = sources
        # Minimal structural representation of Demucs-like architecture
        self.encoder = nn.Sequential(
            nn.Conv1d(2, 16, kernel_size=8, stride=4, padding=2),
            nn.ReLU(),
            nn.Conv1d(16, 32, kernel_size=8, stride=4, padding=2),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose1d(32, 16, kernel_size=8, stride=4, padding=2),
            nn.ReLU(),
            nn.ConvTranspose1d(16, 2 * sources, kernel_size=8, stride=4, padding=2)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch, channels, length)
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        # Reshape to (batch, sources, channels, length)
        batch, _, length = decoded.shape
        return decoded.view(batch, self.sources, 2, length)

class DemucsSeparator:
    def __init__(self, device: str = 'cpu'):
        self.device = torch.device(device)
        self.model = SimpleUNet(sources=4).to(self.device)
        self.model.eval()
        self.source_names = ['drums', 'bass', 'other', 'vocals']

    def separate_audio(self, audio_tensor: torch.Tensor) -> OmniResult:
        """
        Input: Tensor of shape (channels, length), channels usually 2 (stereo)
        Returns dictionary of separated stems
        """
        try:
            if audio_tensor.dim() != 2:
                return OmniResult(err=f"Expected 2D tensor (channels, length), got {audio_tensor.dim()}D")
            
            # Add batch dimension
            x = audio_tensor.unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                # Shape: (1, 4, 2, length)
                stems = self.model(x)
            
            # Remove batch dim
            stems = stems.squeeze(0).cpu()
            
            result = {}
            for i, name in enumerate(self.source_names):
                result[name] = stems[i]
                
            return OmniResult(ok=result)
            
        except Exception as e:
            return OmniResult(err=f"Separation failed: {str(e)}")
