# Omni Diagram of Thought Service (Ruby)
module Omni; module DiagramOfThought
  ROLES = %w[proposer critic summarizer].freeze
  def self.build_dag(propositions, critiques, summaries)
    nodes = propositions.each_with_index.map { |p, i| {id: i, role: 'proposer', content: p} }
    critiques.each_with_index { |c, i| nodes << {id: nodes.size, role: 'critic', content: c, parent: i % [propositions.size, 1].max} }
    summaries.each { |s| nodes << {id: nodes.size, role: 'summarizer', content: s} }
    nodes
  end
  def self.coherence(dag)
    transitions = dag.each_cons(2).count { |a, b| ROLES.include?(a[:role]) && ROLES.include?(b[:role]) }
    transitions.to_f / [dag.size - 1, 1].max
  end
end; end
