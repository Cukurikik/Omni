module Omni
  module DeepSeek
    class ASTValidator
      def validate(ast_json)
        return { error: "Invalid AST" } if ast_json.nil?
        { ok: true }
      end
    end
  end
end
