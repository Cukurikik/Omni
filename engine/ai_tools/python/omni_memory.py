# ==========================================
# 🧠 OMNI NEURAL MEMORY (Phase 33)
# ==========================================
# In-memory Vector Indexer for LLM Context RAG (Retrieval-Augmented Generation)

import math

class OmniVectorDB:
    def __init__(self):
        self.vectors = {}
        print("🧠 [OMNI-MEMORY] Vector Engine Siap. O(1) Fetch.")

    def insert(self, key: str, vector: list):
        # Normalize vector
        magnitude = math.sqrt(sum(x**2 for x in vector))
        self.vectors[key] = [x/magnitude if magnitude > 0 else 0 for x in vector]
    
    def search_closest(self, query: list):
        best_score = -1.0
        best_key = None
        
        # Kosine similarity (Native Python, bisa digantikan oleh Julia)
        for key, vec in self.vectors.items():
            score = sum(q * v for q, v in zip(query, vec))
            if score > best_score:
                best_score = score
                best_key = key
                
        return best_key, best_score

if __name__ == '__main__':
    db = OmniVectorDB()
    db.insert("context_omni", [0.5, 0.8, -0.2])
    db.insert("context_kubernetes", [0.1, -0.8, 0.4])
    
    match, metric = db.search_closest([0.6, 0.7, -0.1])
    print(f"Hasil Eksekusi Memory: {match} (Kepercayaan: {metric:.2f})")
