module Omni
  module Business
    module QuicTransport
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

      class CwndScaling
        def compute_next_cwnd(current_cwnd, bytes_acked, bytes_lost, ssthresh)
          if current_cwnd <= 0
            return OmniResult.new(error: StandardError.new("Congestion window must be strictly positive"))
          end

          # QUIC / TCP NewReno congestion control business logic
          new_cwnd = current_cwnd
          new_ssthresh = ssthresh

          if bytes_lost > 0
            # Multiplicative Decrease (Packet loss detected)
            new_ssthresh = [current_cwnd / 2, 2].max # Minimum 2 MSS
            new_cwnd = new_ssthresh
            return OmniResult.new(value: { cwnd: new_cwnd, ssthresh: new_ssthresh, phase: "CONGESTION_AVOIDANCE" })
          end

          # Additive Increase / Slow Start
          if current_cwnd < ssthresh
            # Slow Start: cwnd grows exponentially
            new_cwnd += bytes_acked
            phase = "SLOW_START"
          else
            # Congestion Avoidance: cwnd grows linearly
            # cwnd += MSS * (bytes_acked / cwnd)
            new_cwnd += [1, bytes_acked / current_cwnd].max
            phase = "CONGESTION_AVOIDANCE"
          end

          OmniResult.new(value: { cwnd: new_cwnd, ssthresh: new_ssthresh, phase: phase })
        end
      end
    end
  end
end
