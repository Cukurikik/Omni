import torch
import torch.nn as nn
from transformers import AutoModel, PreTrainedModel, PretrainedConfig

class OmniLLMTextClassifierConfig(PretrainedConfig):
    model_type = "omni_llm_classifier"
    def __init__(self, base_model="bert-base-uncased", num_classes=2, **kwargs):
        super().__init__(**kwargs)
        self.base_model = base_model
        self.num_classes = num_classes

class OmniLLMTextClassifier(PreTrainedModel):
    """
    OMNI Framework - LLM for Text Classification
    A zero-mock implementation of a fine-tuned LLM structure for classification tasks.
    """
    config_class = OmniLLMTextClassifierConfig

    def __init__(self, config: OmniLLMTextClassifierConfig):
        super().__init__(config)
        self.base_llm = AutoModel.from_pretrained(config.base_model)
        
        # Classification head attached to the pooled output
        hidden_size = self.base_llm.config.hidden_size
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(hidden_size, config.num_classes)
        
        # Initialize weights
        self.post_init()

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        labels=None,
    ):
        outputs = self.base_llm(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )
        
        # Use CLS token representation or pooled output
        pooled_output = outputs.last_hidden_state[:, 0, :]
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)

        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, self.config.num_classes), labels.view(-1))

        return {"loss": loss, "logits": logits}
