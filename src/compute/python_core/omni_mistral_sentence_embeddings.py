import torch
from typing import List, Dict, Any, Optional
from transformers import AutoTokenizer, AutoModel

class Result:
    def __init__(self, value: Any = None, error: Optional[Exception] = None):
        self.value = value
        self.error = error
        self.is_success = error is None

    @classmethod
    def ok(cls, value: Any) -> 'Result':
        return cls(value=value)

    @classmethod
    def fail(cls, error: Exception) -> 'Result':
        return cls(error=error)

class OmniMistralEmbeddingsEngine:
    """
    OMNI Compute Layer: Mistral-based Sentence Embeddings Engine.
    Fine-tuned sentence embedding engine utilizing Mistral-7b architecture.
    Based on kamalkraj/e5-mistral-7b-instruct methodologies.
    """
    def __init__(self, config: Dict[str, Any]):
        self.model_name = config.get("model_name", "intfloat/e5-mistral-7b-instruct")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None

    def initialize(self) -> Result:
        try:
            # We use float16 for efficiency as 7B models are large
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True
            ).to(self.device)
            return Result.ok(True)
        except Exception as e:
            return Result.fail(e)

    def last_token_pool(self, last_hidden_states: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """
        Extracts the embedding of the last token (usually eos or padding) for sequence representation.
        """
        left_padding = (attention_mask[:, -1] == 0)
        if left_padding.any():
            # Handling left padding
            sequence_lengths = attention_mask.sum(1) - 1
            batch_size = last_hidden_states.shape[0]
            return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]
        else:
            return last_hidden_states[:, -1]

    def encode(self, sentences: List[str]) -> Result:
        if not self.model or not self.tokenizer:
            return Result.fail(RuntimeError("Engine not initialized. Call initialize() first."))
            
        try:
            # Prepend instruction for e5-mistral
            task_definition = "Given a web search query, retrieve relevant passages that answer the query"
            processed_texts = [f"Instruct: {task_definition}\nQuery: {text}" for text in sentences]

            # Tokenize
            batch_dict = self.tokenizer(
                processed_texts, 
                max_length=4096, 
                padding=True, 
                truncation=True, 
                return_tensors='pt'
            ).to(self.device)

            self.model.eval()
            with torch.no_grad():
                outputs = self.model(**batch_dict)
                embeddings = self.last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
                
                # Normalize embeddings
                embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
                
            return Result.ok(embeddings)
        except Exception as e:
            return Result.fail(e)

def build_mistral_embeddings_engine() -> Result:
    config = {"model_name": "intfloat/e5-mistral-7b-instruct"}
    engine = OmniMistralEmbeddingsEngine(config)
    return Result.ok(engine)
