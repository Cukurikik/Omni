module Omni
  module Graphics
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

    class CameraNode
      attr_accessor :x, :y, :z, :roll, :pitch, :yaw, :timestamp

      def initialize(x, y, z, r, p, yw, t)
        @x, @y, @z = x, y, z
        @roll, @pitch, @yaw = r, p, yw
        @timestamp = t
      end
    end

    class SceneManager
      def initialize
        @keyframes = []
      end

      def add_keyframe(node)
        begin
          if node.nil? || !node.is_a?(CameraNode)
            return Result.new(error: "Invalid camera node")
          end

          # Enforce chronological ordering
          if @keyframes.any? && node.timestamp <= @keyframes.last.timestamp
            return Result.new(error: "Keyframe timestamp must be strictly increasing")
          end

          @keyframes << node
          Result.new(data: true)
        rescue StandardError => e
          Result.new(error: "Failed to add keyframe: #{e.message}")
        end
      end

      def generate_path_metadata(fps: 30)
        begin
          return Result.new(error: "Not enough keyframes") if @keyframes.size < 2

          total_time = @keyframes.last.timestamp - @keyframes.first.timestamp
          total_frames = (total_time * fps).ceil

          metadata = {
            total_duration: total_time,
            target_fps: fps,
            frame_count: total_frames,
            keyframes_count: @keyframes.size,
            path_type: "Catmull-Rom Spline" # To be computed by Elixir concurrency pool
          }

          Result.new(data: metadata)
        rescue StandardError => e
          Result.new(error: "Metadata generation failed: #{e.message}")
        end
      end
    end
  end
end
