# Omni K2 Geoscience Service (Ruby)
# Ref: davendw49/k2 — Apache-2.0, WSDM 2024
module Omni
  module K2Geoscience
    GEO_KEYWORDS = {
      'seismology' => %w[earthquake seismic fault tremor],
      'mineralogy' => %w[mineral crystal rock gemstone],
      'oceanography' => %w[ocean sea marine current tide],
      'hydrology' => %w[water river aquifer groundwater],
    }.freeze

    def self.classify(question)
      q = question.downcase
      GEO_KEYWORDS.each do |domain, keywords|
        return domain if keywords.any? { |kw| q.include?(kw) }
      end
      'geology'
    end

    def self.format_qa(question, choices)
      opts = choices.each_with_index.map { |c, i| "(#{(65 + i).chr}) #{c}" }.join("\n")
      "Question: #{question}\n#{opts}\nAnswer:"
    end
  end
end
