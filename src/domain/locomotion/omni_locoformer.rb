# omni_locoformer.rb — Generalist Locomotion Service
# Inspired by: locoformer (Generalist Locomotion via Long-Context Adaptation)
# Layer: Domain / Ruby
#
# Domain service integrating context-aware robotic locomotion predictions 
# via gRPC to the Transformer compute layer.

require 'json'
require 'net/http'

module Omni
  module Robotics
    class LocoformerClient
      attr_reader :endpoint, :timeout

      def initialize(endpoint: "http://localhost:8080", timeout: 5)
        @endpoint = endpoint
        @timeout = timeout
      end

      # Sends historical proprioceptive context to generate the next motor commands
      # @param state_history [Array<Hash>] History of joint positions, velocities, and IMU data
      # @param terrain_context [Array<Float>] Environmental terrain embedding
      # @return [Hash] Next target joint positions
      def predict_motor_commands(state_history, terrain_context)
        payload = {
          "context_length" => state_history.length,
          "state_history" => state_history,
          "terrain_embedding" => terrain_context
        }

        response = transmit_request("/api/v1/locomotion/predict", payload)
        
        if response[:success]
          {
            "target_joints" => response[:data]["target_joints"],
            "confidence" => response[:data]["confidence"],
            "adaptation_shift" => response[:data]["adaptation_shift"]
          }
        else
          raise "Locoformer prediction failed: #{response[:error]}"
        end
      end

      private

      def transmit_request(path, payload)
        uri = URI.parse("#{@endpoint}#{path}")
        http = Net::HTTP.new(uri.host, uri.port)
        http.read_timeout = @timeout
        
        request = Net::HTTP::Post.new(uri.request_uri, { 'Content-Type' => 'application/json' })
        request.body = payload.to_json

        begin
          response = http.request(request)
          if response.code == "200"
            { success: true, data: JSON.parse(response.body) }
          else
            { success: false, error: "HTTP #{response.code}: #{response.body}" }
          end
        rescue StandardError => e
          { success: false, error: e.message }
        end
      end
    end

    class LocomotionController
      def initialize(client: LocoformerClient.new)
        @client = client
        @state_buffer = []
        @max_context = 512 # Long-context adaptation
      end

      # Called at every control tick (e.g., 50Hz)
      def tick(current_state, terrain_embedding)
        @state_buffer << current_state
        @state_buffer.shift if @state_buffer.length > @max_context

        commands = @client.predict_motor_commands(@state_buffer, terrain_embedding)
        
        enforce_safety_limits!(current_state, commands["target_joints"])
        
        commands["target_joints"]
      end

      private

      def enforce_safety_limits!(current_state, target_joints)
        # Prevent sudden jerks or exceeding physical hardware limits
        target_joints.each_with_index do |target, idx|
          current = current_state["joints"][idx]
          max_delta = 0.5 # Radians per tick limit
          
          if (target - current).abs > max_delta
            target_joints[idx] = current + (target > current ? max_delta : -max_delta)
          end
        end
      end
    end
  end
end
