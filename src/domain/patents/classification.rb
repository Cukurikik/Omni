#=============================================================================
# OMNI DOMAIN LAYER — US AI PATENTS CLASSIFICATION (RUBY)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Ruby Domain Logic for US AI Patents classification.
# INSPIRED BY: MIRICMILAN/US-AI-Patents
#=============================================================================

require 'json'
require 'omni_bridge/domain'

module Omni
  module Domain
    module Patents
      class PatentClassifier
        attr_reader :model_name

        def initialize(model_name = "patent_bert")
          @model_name = model_name
        end

        # OMNI IDIOM: Monadic Result wrapper
        def classify_patent_text(abstract_text)
          if abstract_text.nil? || abstract_text.empty?
            return Omni::Result.fail("Abstract text cannot be empty")
          end

          # Dispatch classification request to the Compute Layer
          # via Omni Event Loop
          payload = {
            model: @model_name,
            text: abstract_text
          }

          response = Omni::Bridge::EventLoop.call_sync("compute.nlp.classify", payload)

          if response.success?
            format_result(response.data)
          else
            Omni::Result.fail("Classification failed: #{response.error}")
          end
        end

        private

        def format_result(data)
          classification = {
            is_ai_related: data["probability"] > 0.85,
            confidence: data["probability"],
            categories: data["categories"]
          }
          Omni::Result.ok(classification)
        end
      end
    end
  end
end

# rb::route "/api/patents/classify" -> Omni::Domain::Patents::PatentClassifier
