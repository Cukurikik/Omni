# @omni-layer Business | @omni-source yuanzhoulvpi2017/DocumentSearch | @omni-lang Ruby
# @omni-description Document search service: domain layer for corpus management,
# search analytics, relevance feedback, and query logging.

module OmniDocSearchService
  class OmniResult
    attr_reader :data, :error
    def initialize(data: nil, error: nil); @data = data; @error = error; end
    def ok?; @error.nil?; end
  end

  class Corpus
    attr_accessor :id, :name, :n_docs, :n_chunks, :status, :created_at
    def initialize(id:, name:)
      @id = id; @name = name; @n_docs = 0; @n_chunks = 0
      @status = :active; @created_at = Time.now
    end
  end

  class QueryLog
    attr_accessor :query, :corpus_id, :top_k, :latency_ms, :n_results, :timestamp
    def initialize(query:, corpus_id:, top_k:, latency_ms:, n_results:)
      @query = query; @corpus_id = corpus_id; @top_k = top_k
      @latency_ms = latency_ms; @n_results = n_results; @timestamp = Time.now
    end
  end

  class DocumentSearchService
    def initialize
      @corpora = {}
      @query_logs = []
      @feedback = []
    end

    def create_corpus(id:, name:)
      @corpora[id] = Corpus.new(id: id, name: name)
      OmniResult.new(data: { corpus_id: id, name: name })
    rescue => e
      OmniResult.new(error: e.message)
    end

    def update_corpus_stats(corpus_id:, n_docs:, n_chunks:)
      corpus = @corpora[corpus_id]
      return OmniResult.new(error: "Corpus not found") unless corpus
      corpus.n_docs = n_docs
      corpus.n_chunks = n_chunks
      OmniResult.new(data: { corpus_id: corpus_id, n_docs: n_docs, n_chunks: n_chunks })
    rescue => e
      OmniResult.new(error: e.message)
    end

    def log_query(query:, corpus_id:, top_k:, latency_ms:, n_results:)
      log = QueryLog.new(query: query, corpus_id: corpus_id, top_k: top_k, latency_ms: latency_ms, n_results: n_results)
      @query_logs << log
      OmniResult.new(data: { logged: true, total_queries: @query_logs.size })
    rescue => e
      OmniResult.new(error: e.message)
    end

    def record_feedback(query:, doc_id:, relevant:)
      @feedback << { query: query, doc_id: doc_id, relevant: relevant, timestamp: Time.now }
      OmniResult.new(data: { total_feedback: @feedback.size })
    rescue => e
      OmniResult.new(error: e.message)
    end

    def search_analytics
      return OmniResult.new(data: { total_queries: 0 }) if @query_logs.empty?
      latencies = @query_logs.map(&:latency_ms)
      OmniResult.new(data: {
        total_queries: @query_logs.size,
        avg_latency_ms: latencies.sum / latencies.size.to_f,
        p95_latency_ms: latencies.sort[(latencies.size * 0.95).to_i],
        avg_results: @query_logs.map(&:n_results).sum / @query_logs.size.to_f,
        total_feedback: @feedback.size,
        relevance_rate: @feedback.empty? ? 0 : @feedback.count { |f| f[:relevant] }.to_f / @feedback.size
      })
    rescue => e
      OmniResult.new(error: e.message)
    end

    def stats
      { corpora: @corpora.size, queries: @query_logs.size, feedback: @feedback.size }
    end
  end
end
