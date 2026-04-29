# OMNI Engine: Aktiva Rules
# Ruby Convention-over-configuration Domain Layer for mathematical asset boundary verification.

module Omni
  module Domain
    module AktivaRules

      class AktivaError < StandardError; end

      class Result
        attr_reader :value, :error

        def initialize(value, error)
          @value = value
          @error = error
        end

        def self.ok(value)
          new(value, nil)
        end

        def self.err(msg)
          new(nil, AktivaError.new(msg))
        end

        def ok?
          @error.nil?
        end

        def unwrap!
          raise @error unless ok?
          @value
        end
      end

      class AssetPolicy
        def initialize(max_drawdown: 0.15)
          @max_drawdown = max_drawdown
        end

        def enforce_drawdown_limit(current_value, peak_value)
          if current_value < 0.0 || peak_value < 0.0
            return Result.err("Financial singularity: values cannot be mathematically negative constraints")
          end

          if peak_value == 0.0
             return Result.err("Degenerate peak geometry: Division by zero avoided")
          end

          drawdown = (peak_value - current_value) / peak_value

          if drawdown > @max_drawdown
             return Result.err("Asset liquidation triggered: Drawdown #{drawdown} exceeds hard boundary #{@max_drawdown}")
          end

          Result.ok({ drawdown: drawdown, status: "stable" })
        end

        def validate_portfolio_rebalance(weights_vector)
           if weights_vector.empty?
              return Result.err("Degenerate portfolio state")
           end
           
           sum = weights_vector.reduce(0.0) { |acc, val| acc + val }
           if (sum - 1.0).abs > 0.01
              return Result.err("Mathematical topology violation: weights do not construct unit space 1.0")
           end
           
           Result.ok(true)
        end
      end

    end
  end
end
