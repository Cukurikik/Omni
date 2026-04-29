import numpy as np

class Code2VecModel:
    def __init__(self, vocab_size, embed_dim):
        self.path_embeddings = np.random.randn(vocab_size, embed_dim)
        self.context_matrix = np.random.randn(embed_dim, embed_dim)
        
    def embed_method(self, ast_paths):
        # Aggregate path embeddings to form method embedding
        path_vecs = [self.path_embeddings[p] for p in ast_paths if p < len(self.path_embeddings)]
        if not path_vecs:
            return np.zeros(self.path_embeddings.shape[1])
        
        # Simple attention mechanism proxy
        weighted_sum = np.sum(path_vecs, axis=0)
        return np.tanh(np.dot(self.context_matrix, weighted_sum))
