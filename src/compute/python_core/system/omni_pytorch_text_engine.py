import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OmniPyTorchTextEngine:
    """
    OMNI Engine for PyTorch Text (torchtext).
    Provides monadic data pipelines, tokenization, and numericalization wrappers 
    for NLP workflows natively.
    """

    def __init__(self, vocab_path: str = None):
        """Initialize PyTorchText engine with default configuration."""
        self.vocab_path = vocab_path
        self.vocab = None
        self.tokenizer = None

    def initialize_tokenizer(self, language: str = 'en') -> Dict[str, Any]:
        """
        Initializes a basic torchtext tokenizer (e.g., basic_english).
        """
        if not language:
            return {"status": "error", "message": "Language code required"}
            
        if language != "en":
            return {"status": "error", "message": f"Unsupported tokenizer language structure for {language}"}
            
        try:
            import torchtext
            from torchtext.data.utils import get_tokenizer
            
            self.tokenizer = get_tokenizer("basic_english")
            return {"status": "success", "message": f"Tokenizer {language} initialized"}
        except ImportError as e:
            return {"status": "error", "message": f"Missing torchtext module: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def build_vocabulary(self, iterator: Any) -> Dict[str, Any]:
        """
        Builds a TorchText vocab object from a given text iterator.
        """
        if self.tokenizer is None:
            return {"status": "error", "message": "Tokenizer not initialized"}
            
        if iterator is None:
            return {"status": "error", "message": "Iterator cannot be None"}
            
        try:
            from torchtext.vocab import build_vocab_from_iterator
            
            def yield_tokens(data_iter):
                for text in data_iter:
                    yield self.tokenizer(text)
                    
            self.vocab = build_vocab_from_iterator(yield_tokens(iterator), specials=["<unk>"])
            self.vocab.set_default_index(self.vocab["<unk>"])
            
            return {"status": "success", "vocab_size": len(self.vocab)}
        except ImportError:
            return {"status": "error", "message": "torchtext.vocab module missing"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def process_text_to_tensor(self, text: str) -> Dict[str, Any]:
        """
        Converts a raw string into a PyTorch tensor representation using the built vocab.
        """
        if not text:
            return {"status": "error", "message": "Text cannot be empty"}
            
        if self.vocab is None or self.tokenizer is None:
            return {"status": "error", "message": "Vocabulary and Tokenizer must be initialized first"}
            
        try:
            import torch
            tokens = self.tokenizer(text)
            indices = self.vocab(tokens)
            tensor_repr = torch.tensor(indices, dtype=torch.long)
            
            return {"status": "success", "tensor_length": len(tensor_repr)}
        except ImportError:
            return {"status": "error", "message": "torch module missing"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def diagnostics(self) -> Dict[str, Any]:
        """Returns engine health status for the OmniEngineRegistry."""
        return {
            "engine": "OmniPyTorchTextEngine",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": ["initialize_tokenizer", "build_vocabulary", "process_text_to_tensor"],
            "vocab_loaded": self.vocab is not None,
            "tokenizer_loaded": self.tokenizer is not None,
        }
