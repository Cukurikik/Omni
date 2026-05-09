#=============================================================================
# OMNI COMPUTE LAYER — DIFFERENTIAL TRANSFORMER MODEL (PYTHON)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Assembles the full Differential Transformer network.
#=============================================================================

import numpy as np
import omni_bridge.domain.error as err
import omni_bridge.system.tensor as tensor_ffi
from .diff_transformer_layer import DiffTransformerLayer

class DiffTransformer:
    """
    Full Differential Transformer Model.
    """
    def __init__(self, vocab_size: int, d_model: int, n_heads: int, num_layers: int):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.n_heads = n_heads
        self.num_layers = num_layers
        
        # In Omni, layers are allocated in continuous memory pools
        self.layers = [DiffTransformerLayer(d_model, n_heads) for _ in range(num_layers)]

    def generate(self, input_ids: np.ndarray, max_new_tokens: int) -> err.Result[np.ndarray]:
        try:
            current_ids = input_ids
            
            for _ in range(max_new_tokens):
                # 1. Embedding lookup (bridged to C++ for speed)
                embeddings = tensor_ffi.embedding_lookup(current_ids, self.d_model)
                
                # 2. Add Positional Encoding
                x = tensor_ffi.add_positional_encoding(embeddings)
                
                # 3. Forward pass through all layers
                for layer in self.layers:
                    layer_result = layer.forward(x)
                    if not layer_result.is_success():
                        return layer_result # Propagate error
                    x = layer_result.unwrap()
                
                # 4. Final RMSNorm
                x_norm = tensor_ffi.execute_rmsnorm(x)
                
                # 5. LM Head (Logits)
                # Take the last token's representation
                last_token_repr = x_norm[:, -1, :] 
                logits = tensor_ffi.linear_proj_lm_head(last_token_repr, self.vocab_size)
                
                # 6. Sample token (Argmax for greedy decoding)
                next_token = np.argmax(logits, axis=-1).reshape(-1, 1)
                
                # Append to sequence
                current_ids = np.concatenate([current_ids, next_token], axis=1)
                
            return err.Ok(current_ids)
            
        except Exception as e:
            return err.Err(f"DiffTransformer generation failed: {str(e)}")
