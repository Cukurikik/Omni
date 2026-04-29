module Omni
  module Optimization
    class LossLandscapeTracker
      attr_reader :history, :divergence_threshold

      def initialize(divergence_threshold: 1000.0)
        @history = []
        @divergence_threshold = divergence_threshold
      end

      # Monadic Result pattern implementation in Ruby
      class Result
        attr_reader :data, :error

        def initialize(data: nil, error: nil)
          @data = data
          @error = error
        end

        def ok?
          @error.nil?
        end

        def unwrap
          raise "Unwrap failed: #{@error}" unless ok?
          @data
        end
      end

      def record_epoch(epoch, loss, params_snapshot)
        begin
          if loss.nil? || loss.nan?
            return Result.new(error: "Loss cannot be NaN or nil at epoch #{epoch}")
          end

          if loss > @divergence_threshold
            return Result.new(error: "Divergence detected: Loss #{loss} exceeded threshold #{@divergence_threshold}")
          end

          record = {
            epoch: epoch,
            loss: loss,
            params: params_snapshot,
            timestamp: Time.now.utc.to_i
          }

          @history << record
          Result.new(data: :recorded)
        rescue StandardError => e
          Result.new(error: "Failed to record epoch: #{e.message}")
        end
      end

      def detect_plateau(window_size: 10, tolerance: 1e-4)
        begin
          return Result.new(data: false) if @history.size < window_size

          recent_losses = @history.last(window_size).map { |r| r[:loss] }
          max_loss = recent_losses.max
          min_loss = recent_losses.min

          is_plateau = (max_loss - min_loss) < tolerance
          Result.new(data: is_plateau)
        rescue StandardError => e
          Result.new(error: "Plateau detection failed: #{e.message}")
        end
      end

      def export_trajectory
        begin
          Result.new(data: @history)
        rescue StandardError => e
          Result.new(error: "Failed to export trajectory: #{e.message}")
        end
      end
    end
  end
end
