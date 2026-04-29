import torch
import torch.nn as nn
from typing import List
from omni_core.result import OmniResult, Ok, Err

class LSTMMidiGenerator(nn.Module):
    """
    OMNI COMPUTE LAYER: Generative Jazz
    LSTM network trained on MIDI sequences to generate jazz melodies.
    """
    def __init__(self, vocab_size: int = 128, embed_dim: int = 64, hidden_dim: int = 256):
        super(LSTMMidiGenerator, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers=2, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x: torch.Tensor, hidden=None):
        embedded = self.embedding(x)
        out, hidden = self.lstm(embedded, hidden)
        out = self.fc(out)
        return out, hidden

class JazzEngine:
    def __init__(self, model: LSTMMidiGenerator):
        self.model = model
        self.model.eval()

    def generate_sequence(self, seed_notes: List[int], length: int = 50, temperature: float = 1.0) -> OmniResult[List[int], str]:
        try:
            current_seq = torch.tensor([seed_notes], dtype=torch.long)
            generated = list(seed_notes)
            hidden = None

            with torch.no_grad():
                for _ in range(length):
                    output, hidden = self.model(current_seq, hidden)
                    # Get logits for the last step
                    logits = output[0, -1, :] / temperature
                    probs = torch.softmax(logits, dim=0)
                    
                    # Sample from the distribution
                    next_note = torch.multinomial(probs, 1).item()
                    generated.append(next_note)
                    
                    # Next input
                    current_seq = torch.tensor([[next_note]], dtype=torch.long)

            return Ok(generated)
        except Exception as e:
            return Err(f"Jazz generation failed: {str(e)}")
