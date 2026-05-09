#=============================================================================
# OMNI DOMAIN LAYER — SENTIMENT RULE PARSER (RUBY)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Ruby DSL for defining dynamic business rules over Sentiment data.
#=============================================================================

module Omni
  module Domain
    module NLP
      class SentimentRuleParser
        # OMNI IDIOM: rb::route / Ruby DSL
        
        def initialize(&block)
          @rules = []
          instance_eval(&block) if block_given?
        end

        def on_negative_sentiment(threshold:, &action)
          @rules << {
            condition: ->(sentiment) { sentiment.negative_score >= threshold },
            action: action,
            type: :negative
          }
        end

        def on_positive_sentiment(threshold:, &action)
          @rules << {
            condition: ->(sentiment) { sentiment.positive_score >= threshold },
            action: action,
            type: :positive
          }
        end

        def evaluate(sentiment_record)
          @rules.each do |rule|
            if rule[:condition].call(sentiment_record)
              # Fire action within the OMNI Event Loop
              rule[:action].call(sentiment_record)
            end
          end
        end
      end
    end
  end
end

# Example DSL Usage within Domain Logic:
#
# parser = Omni::Domain::NLP::SentimentRuleParser.new do
#   on_negative_sentiment(threshold: 0.8) do |record|
#     Omni::Bridge::EventLoop.call_async("network.alerts.send", { message: "Critical negative feedback: #{record.text_id}" })
#   end
# end
