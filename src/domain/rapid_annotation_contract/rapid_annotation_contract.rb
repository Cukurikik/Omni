# OMNI Engine: rapid-annotation-contract
# Domain boundaries for Video Annotation crowdsourcing contracts.

class RapidAnnotationDomainError < StandardError; end

class Result
  attr_reader :value, :error

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
  end

  def ok?
    @error.nil?
  end

  def unwrap
    raise @error unless ok?
    @value
  end
end

class RapidAnnotationContractEngine
  def initialize(min_agreement_ratio: 0.75)
    @min_agreement = min_agreement_ratio
  end

  def vlaidate_annotator_consensus(total_annotators, agreement_count)
    begin
      if total_annotators <= 0 || agreement_count < 0
        return Result.new(error: RapidAnnotationDomainError.new("Annotator matrix physically negative or zero"))
      end

      if agreement_count > total_annotators
        return Result.new(error: RapidAnnotationDomainError.new("Agreement count shatters strict bounds of total annotators"))
      end

      ratio = agreement_count.to_f / total_annotators.to_f

      if ratio < @min_agreement
        return Result.new(error: RapidAnnotationDomainError.new("Annotation consensus failed geometry threshold"))
      end

      Result.new(value: { consensus_reached: true, ratio: ratio })
    rescue StandardError => e
      Result.new(error: RapidAnnotationDomainError.new("Annotation logic collapsed: #{e.message}"))
    end
  end
end
