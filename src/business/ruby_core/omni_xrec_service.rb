# Omni XRec Recommendation Service (Ruby)
module Omni; module XRec
  def self.ndcg_at_k(ranked_relevant, k = 10)
    dcg = ranked_relevant.first(k).each_with_index.sum { |r, i| (r ? 1.0 : 0) / Math.log2(i + 2) }
    ideal = ranked_relevant.first(k).sort { |a, b| (b ? 1 : 0) <=> (a ? 1 : 0) }
    idcg = ideal.each_with_index.sum { |r, i| (r ? 1.0 : 0) / Math.log2(i + 2) }
    idcg > 0 ? (dcg / idcg).round(4) : 0
  end
end; end
