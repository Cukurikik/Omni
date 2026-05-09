import torch
import torch.nn as nn

class OmniMoELLaVAEncoder(nn.Module):
    """
    OMNI Framework - Mixture of Experts Large Vision-Language Model (MoE-LLaVA)
    Maps visual patches into the LLM embedding space. Features an MoE mechanism 
    within the vision-language projector itself to handle diverse image modalities
    (e.g., natural images, documents, charts).
    Inspired by PKU-YuanGroup/MoE-LLaVA.
    """
    def __init__(self, vision_dim: int, llm_dim: int, num_projector_experts: int = 4):
        super().__init__()
        self.vision_dim = vision_dim
        self.llm_dim = llm_dim
        self.num_experts = num_projector_experts
        
        # Router for visual patches
        self.router = nn.Linear(vision_dim, num_projector_experts)
        
        # Multimodal Projector Experts (e.g., Expert 0: Natural, Expert 1: Document OCR)
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(vision_dim, llm_dim),
                nn.GELU(),
                nn.Linear(llm_dim, llm_dim)
            ) for _ in range(num_projector_experts)
        ])

        print(f"OMNI Python: Initialized MoE-LLaVA Vision Projector with {num_projector_experts} experts.")

    def forward(self, image_features: torch.Tensor) -> torch.Tensor:
        """
        image_features: [batch_size, num_patches, vision_dim] (e.g., from CLIP ViT-L/14)
        """
        batch_size, num_patches, _ = image_features.shape
        flat_features = image_features.view(-1, self.vision_dim)
        
        # Calculate routing probabilities for each visual patch
        router_logits = self.router(flat_features)
        routing_probs = torch.softmax(router_logits, dim=-1)
        
        # Select Top-1 expert for each patch for efficiency in the projector
        max_probs, expert_indices = torch.max(routing_probs, dim=-1)
        
        output_features = torch.zeros((batch_size * num_patches, self.llm_dim), device=image_features.device)
        
        for i, expert in enumerate(self.experts):
            # Mask for patches routed to expert i
            patch_mask = (expert_indices == i)
            if patch_mask.any():
                expert_input = flat_features[patch_mask]
                # Apply projection and multiply by router probability
                expert_output = expert(expert_input) * max_probs[patch_mask].unsqueeze(-1)
                output_features[patch_mask] = expert_output
                
        return output_features.view(batch_size, num_patches, self.llm_dim)
