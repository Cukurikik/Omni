# OMNI Framework - Milvus Vector Search (Python)
# High-performance similarity search for Retrieval-Augmented Generation (RAG)

from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility

class OmniMilvusSearch:
    def __init__(self, host="localhost", port="19530", collection_name="omni_knowledge"):
        print(f"OMNI Python: Connecting to Milvus at {host}:{port}...")
        connections.connect("default", host=host, port=port)
        self.collection_name = collection_name
        self._ensure_collection()
        self.collection = Collection(self.collection_name)
        self.collection.load()

    def _ensure_collection(self):
        if not utility.has_collection(self.collection_name):
            print(f"OMNI Python: Creating collection {self.collection_name}...")
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535)
            ]
            schema = CollectionSchema(fields, "OMNI RAG Knowledge Base")
            col = Collection(self.collection_name, schema)
            
            # Create Index
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            col.create_index(field_name="embedding", index_params=index_params)

    def search(self, query_vector: list, top_k: int = 5):
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.collection.search(
            data=[query_vector], 
            anns_field="embedding", 
            param=search_params,
            limit=top_k, 
            output_fields=["text"]
        )
        return results

# Example Usage
# if __name__ == "__main__":
#     db = OmniMilvusSearch()
#     res = db.search([0.1]*768)
#     print(res)
