import json
import numpy as np

class OmniEmojeezEngine:
    """
    AI-powered semantic search engine for emojis.
    Maps a text query into an embedding space and retrieves the closest emojis.
    """
    def __init__(self, emoji_data_path: str):
        # In a real scenario, this loads a Qdrant or FAISS index of emoji embeddings
        self.emoji_db = []
        self.embeddings = []
        self._load_data(emoji_data_path)

    def _load_data(self, path):
        """Mock loader for emoji embeddings."""
        # Represents id, emoji, description, and a 128D embedding
        self.emoji_db = [
            {"emoji": "🔥", "desc": "fire, hot, lit"},
            {"emoji": "😢", "desc": "crying, sad, tears"},
            {"emoji": "🚀", "desc": "rocket, launch, to the moon"}
        ]
        # Random mock embeddings for demonstration
        self.embeddings = np.random.rand(3, 128)
        self.embeddings /= np.linalg.norm(self.embeddings, axis=1, keepdims=True)

    def _get_text_embedding(self, text: str) -> np.ndarray:
        """Mock LLM embedding generation."""
        vec = np.random.rand(128)
        return vec / np.linalg.norm(vec)

    def search_emoji(self, query: str, top_k: int = 1) -> list[str]:
        """
        Performs Cosine Similarity search over the emoji embeddings.
        """
        query_vec = self._get_text_embedding(query)
        
        # Cosine similarity
        similarities = np.dot(self.embeddings, query_vec)
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [self.emoji_db[i]["emoji"] for i in top_indices]

# Test
if __name__ == "__main__":
    engine = OmniEmojeezEngine("mock_path")
    print("Semantic Emoji for 'I am launching a startup':", engine.search_emoji("launching a startup"))
