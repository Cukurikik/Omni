from omni.core import Result, Ok, Err

def retrieve_rag_documents(query: str) -> Result[list, Exception]:
    if not query:
        return Err(ValueError("Query empty"))
    return Ok(["doc1", "doc2"])
