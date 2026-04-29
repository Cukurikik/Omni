# Omni Dottxt Prompt Router (Ruby)
# Domain Layer: Strict pattern matching for routing raw prompts to correct specialized LLMs.

module Omni
  module Dottxt
    class PromptRouter
      
      Result = Struct.new(:success, :target_model, :error)

      def self.route(prompt_text)
        return Result.new(false, nil, "Prompt text cannot be empty") if prompt_text.nil? || prompt_text.strip.empty?

        case prompt_text
        when /math|calculate|equation/i
          Result.new(true, "omni-math-instruct-v1", nil)
        when /code|function|debug/i
          Result.new(true, "omni-coder-base-v2", nil)
        else
          Result.new(true, "omni-general-chat-v3", nil)
        end
      end
      
    end
  end
end
