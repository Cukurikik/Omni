require 'json'

# OMNI QWEN: Tool Use & ReAct Extractor
# Ruby logic to parse tool-call syntax (Thought, Action, Action Input) from Qwen's text output.
# Source: QwenLM/Qwen

module Omni
  module Qwen
    class ExtractorError < StandardError; end

    class ToolCall
      attr_reader :thought, :action, :arguments

      def initialize(thought, action, arguments)
        @thought = thought
        @action = action
        @arguments = arguments
      end
    end

    class ReActExtractor
      # Regex patterns based on Qwen's specific tool-use prompt templates
      THOUGHT_PATTERN = /Thought:\s*(.*?)(?=Action:|$)/m
      ACTION_PATTERN = /Action:\s*([^\n]+)/
      ACTION_INPUT_PATTERN = /Action Input:\s*(\{.*?\})/m

      def self.extract(llm_output)
        # Parse Thought
        thought_match = llm_output.match(THOUGHT_PATTERN)
        thought = thought_match ? thought_match[1].strip : ""

        # Parse Action Name
        action_match = llm_output.match(ACTION_PATTERN)
        return nil unless action_match # If no Action is specified, it's a normal conversational response
        action_name = action_match[1].strip

        # Parse Action Input (JSON)
        input_match = llm_output.match(ACTION_INPUT_PATTERN)
        arguments = {}
        
        if input_match
          begin
            arguments = JSON.parse(input_match[1].strip)
          rescue JSON::ParserError
            raise ExtractorError, "Failed to parse Action Input as valid JSON"
          end
        end

        ToolCall.new(thought, action_name, arguments)
      end
    end
  end
end

# Usage:
# output = "Thought: I need to calculate the weather. \nAction: get_weather \nAction Input: {\"location\": \"Tokyo\"}"
# call = Omni::Qwen::ReActExtractor.extract(output)
# puts call.action # => "get_weather"
