# OMNI FASTCHAT: Model Selector Logic
# Ruby business logic mimicking FastChat's Arena model selection criteria.
# Given a user prompt and system constraints, selects the most appropriate model to answer.
# Source: lm-sys/FastChat

module Omni
  module FastChat
    class SelectorError < StandardError; end

    class ModelProfile
      attr_reader :name, :context_window, :is_multimodal, :license

      def initialize(name, context_window, is_multimodal, license)
        @name = name
        @context_window = context_window
        @is_multimodal = is_multimodal
        @license = license
      end
    end

    class ModelSelector
      def initialize
        @models = []
      end

      def register_model(profile)
        @models << profile
      end

      def select_best_model(user_prompt, requires_commercial_use: false, contains_image: false)
        raise SelectorError, "No models registered" if @models.empty?

        # 1. Estimate tokens (dummy 4 chars = 1 token)
        estimated_tokens = user_prompt.length / 4

        # 2. Filter available models based on constraints
        candidates = @models.select do |m|
          fits_context = m.context_window >= estimated_tokens
          meets_commercial = requires_commercial_use ? (m.license == "Apache-2.0" || m.license == "MIT") : true
          meets_multimodal = contains_image ? m.is_multimodal : true

          fits_context && meets_commercial && meets_multimodal
        end

        raise SelectorError, "No suitable model found for the given constraints" if candidates.empty?

        # 3. Sort by some heuristic (e.g., largest context window wins, or pick specifically optimized models)
        # Here we just pick the one with the smallest sufficient context window to save compute.
        candidates.sort_by { |m| m.context_window }.first.name
      end
    end
  end
end

# Usage:
# selector = Omni::FastChat::ModelSelector.new
# selector.register_model(Omni::FastChat::ModelProfile.new("llama-2-7b", 4096, false, "Llama-2"))
# selector.register_model(Omni::FastChat::ModelProfile.new("llava-1.5", 4096, true, "Apache-2.0"))
# best = selector.select_best_model("Describe this image.", contains_image: true, requires_commercial_use: true)
# puts best # => "llava-1.5"
