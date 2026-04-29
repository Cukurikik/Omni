module Omni
  module Business
    module FederatedLearning
      class OmniResult
        attr_reader :value, :error
        
        def initialize(value: nil, error: nil)
          @value = value
          @error = error
        end
        
        def ok?
          @error.nil?
        end
      end

      class ClientSelection
        def initialize(min_clients_required: 3)
          @min_clients = min_clients_required
        end

        def select_clients(available_clients: Array, fraction: Float)
          if available_clients.nil? || available_clients.empty?
            return OmniResult.new(error: StandardError.new("No clients available"))
          end

          if fraction <= 0.0 || fraction > 1.0
            return OmniResult.new(error: StandardError.new("Fraction must be between 0 and 1"))
          end

          target_count = [ (available_clients.size * fraction).ceil, @min_clients ].max
          
          if target_count > available_clients.size
            return OmniResult.new(error: StandardError.new("Not enough available clients to satisfy minimum requirements"))
          end

          # Deterministic selection for production (sort and take)
          selected = available_clients.sort_by { |c| c[:id] }.take(target_count)

          OmniResult.new(value: selected)
        end
      end
    end
  end
end
