import torch
import torch.nn as nn
from transformers import AutoModel, AutoConfig

class OmniStanceKEMLM(nn.Module):
    """
    OMNI Framework Implementation of Knowledge Enhanced Masked Language Model 
    for Stance Detection (GU-DataLab/stance-detection-KE-MLM)
    """
    def __init__(self, model_name="bert-base-uncased", num_labels=3):
        super().__init__()
        self.config = AutoConfig.from_pretrained(model_name)
        self.bert = AutoModel.from_pretrained(model_name)
        
        # Knowledge enhancement layer (injects external knowledge graph embeddings)
        self.knowledge_gate = nn.Linear(self.config.hidden_size * 2, self.config.hidden_size)
        
        # Classification head for Stance (Favor, Against, None)
        self.classifier = nn.Sequential(
            nn.Dropout(0.1),
            nn.Linear(self.config.hidden_size, num_labels)
        )

    def forward(self, input_ids, attention_mask, knowledge_embeddings):
        # Base representation
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        
        # Merge linguistic and knowledge features
        gated_features = torch.sigmoid(
            self.knowledge_gate(torch.cat([pooled_output, knowledge_embeddings], dim=1))
        )
        enhanced_output = pooled_output * gated_features
        
        logits = self.classifier(enhanced_output)
        return logits
