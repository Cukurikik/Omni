"""
populate_vector_store.py
Populate Qdrant dengan seluruh katalog teknologi Omni-Guru
sehingga LLM dapat melakukan semantic lookup.
"""
import pathlib
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

CATALOG_FILE = pathlib.Path(__file__).parent / "catalog.txt"
QDRANT_URL = "http://localhost:6333"
COLLECTION = "tech_catalog"

def main():
    if not CATALOG_FILE.exists():
        print(f"ERROR: {CATALOG_FILE} not found. Generate it first.")
        return

    lines = [l.strip() for l in CATALOG_FILE.read_text().splitlines() if l.strip()]
    print(f"Loaded {len(lines)} terms from catalog.")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    vectors = model.encode(lines, show_progress_bar=True).tolist()

    client = QdrantClient(url=QDRANT_URL)

    # Recreate collection
    client.recreate_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    # Upload in batches of 100
    batch_size = 100
    for i in range(0, len(lines), batch_size):
        batch_lines = lines[i:i+batch_size]
        batch_vecs = vectors[i:i+batch_size]
        points = [
            PointStruct(id=i+j, vector=v, payload={"term": t})
            for j, (t, v) in enumerate(zip(batch_lines, batch_vecs))
        ]
        client.upsert(collection_name=COLLECTION, points=points)
        print(f"Uploaded {i+len(batch_lines)}/{len(lines)} terms...")

    print(f"Done! Collection '{COLLECTION}' has {len(lines)} entries.")

def search(query: str, top_k: int = 5) -> list[str]:
    """Semantic search — used by Omni-Guru LLM function `search_catalog`."""
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = QdrantClient(url=QDRANT_URL)
    qvec = model.encode([query])[0].tolist()
    results = client.search(collection_name=COLLECTION, query_vector=qvec, limit=top_k)
    return [r.payload["term"] for r in results]

if __name__ == "__main__":
    main()
