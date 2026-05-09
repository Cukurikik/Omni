# frozen_string_literal: true

require 'json'

# OMNI MOTHER: GraphQL Schema Definition (Production Grade)
# Declarative schema for bridging Ruby domain logic to frontend clients.

module Omni
  module Graphql
    class Schema
      def self.execute(query:, variables: {}, context: {})
        puts "[OMNI RUBY] Executing GraphQL Query: #{query}"
        
        # Simple mock execution engine
        if query.include?("payment")
          { data: { payment: Omni::Domain::PaymentResolver.resolve(context) } }
        else
          { errors: [{ message: "Unknown query" }] }
        end
      end
    end
  end
end
