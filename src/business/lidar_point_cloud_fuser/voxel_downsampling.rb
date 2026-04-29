module Omni
  module Business
    module LidarPointCloudFuser
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

      class VoxelDownsampling
        def determine_voxel_size(point_count, is_highway_speed)
          if point_count <= 0
            return OmniResult.new(error: StandardError.new("Point count must be positive"))
          end

          # LiDAR Business Logic: Voxel Grid Downsampling Rules
          # A raw Velodyne LiDAR generates millions of points per second. Processing them all
          # is impossible in real-time. We group points into 3D boxes (Voxels) to compress the data.
          
          voxel_size_cm = 5.0 # Base resolution 5cm
          
          # If moving at highway speeds, we need to process frames faster, so we drop resolution
          if is_highway_speed
             voxel_size_cm = 20.0 # Fast driving needs 20cm resolution for speed
          end
          
          # If the point cloud is insanely dense, increase voxel size to save compute
          if point_count > 2_000_000
             voxel_size_cm = [voxel_size_cm, 10.0].max
          end
          
          OmniResult.new(value: { voxel_size_cm: voxel_size_cm })
        end
      end
    end
  end
end
