"""
moe_mixtral_visualizer.py — Interface / Analytics
Layer: UI / Analytics — Expert Choice Visualization

Visualizes the expert routing choices made by an MoE model (like Mixtral 8x7B)
during text generation. Plots a heatmap showing which experts were selected
for each token in a generated sequence.
"""
import torch
import numpy as np
from typing import List, Tuple
# Note: In a real environment, matplotlib would be imported.
# import matplotlib.pyplot as plt

class MixtralExpertVisualizer:
    """
    Captures and visualizes routing choices across MoE layers.
    """
    def __init__(self, num_layers: int, num_experts: int):
        self.num_layers = num_layers
        self.num_experts = num_experts
        
        # History: List of tensors shape (seq_len, num_layers) containing the chosen expert ID
        self.routing_history: List[torch.Tensor] = []
        self.tokens: List[str] = []

    def log_routing_decision(self, layer_idx: int, chosen_expert: int):
        """Used internally during generation hooks to log choices."""
        pass # Actual hook implementation omitted for brevity

    def inject_history(self, tokens: List[str], expert_indices: torch.Tensor):
        """
        Inject completed history for visualization.
        expert_indices: (seq_len, num_layers) containing integer IDs 0 to num_experts-1
        """
        self.tokens = tokens
        self.routing_history = expert_indices

    def render_heatmap_console(self):
        """
        Renders a lightweight text-based heatmap to the console since 
        we cannot easily display matplotlib images in a terminal.
        """
        if len(self.tokens) == 0:
            print("No routing history to display.")
            return
            
        print("\n--- MoE Expert Routing Heatmap ---")
        print("Columns: Layers | Rows: Tokens | Cell: Expert ID")
        
        header = "Token".ljust(15) + "| " + " ".join([f"L{i:<2}" for i in range(self.num_layers)])
        print(header)
        print("-" * len(header))
        
        for t_idx, token in enumerate(self.tokens):
            # Clean up token string for display
            display_tok = token.replace("\n", "\\n")[:12].ljust(15)
            
            row_str = display_tok + "| "
            for l_idx in range(self.num_layers):
                expert_id = self.routing_history[t_idx, l_idx].item()
                row_str += f"{expert_id:<3}"
                
            print(row_str)
        print("-" * len(header))

# Usage Example
if __name__ == "__main__":
    visualizer = MixtralExpertVisualizer(num_layers=4, num_experts=8)
    
    # Mock data
    tokens = ["The", "quick", "brown", "fox", "jumps", "over"]
    # Random expert choices
    choices = torch.randint(0, 8, (len(tokens), 4))
    
    visualizer.inject_history(tokens, choices)
    visualizer.render_heatmap_console()
