# autollm — RAG Document Routes
class AutoLLMRoutes
  MAX_DOCS = 100000

  def self.create_index(name, embedding_model)
    return { ok: false, error: "Missing index name" } unless name && !name.empty?
    return { ok: false, error: "Missing embedding model" } unless embedding_model && !embedding_model.empty?
    return { ok: false, error: "Name too long" } if name.length > 256
    { ok: true, value: { index: name, model: embedding_model } }
  end

  def self.query_index(index_name, query, top_k = 5)
    return { ok: false, error: "Missing index" } unless index_name
    return { ok: false, error: "Empty query" } unless query && !query.empty?
    return { ok: false, error: "top_k out of range" } if top_k < 1 || top_k > 100
    { ok: true, value: { index: index_name, results: top_k } }
  end
end
