import omni

def search_milvus(query_vector: list) -> omni.Result:
    return omni.Result.Ok({"hits": []})
