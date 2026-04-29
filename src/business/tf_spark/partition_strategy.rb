# OMNI TF-SPARK: Partition Strategy
# Ruby logic implementing data partitioning strategies to align Spark RDD partitions 
# with TensorFlow worker nodes for optimal localized training.
# Source: yahoo/TensorFlowOnSpark

module Omni
  module TFSpark
    class PartitionError < StandardError; end

    class PartitionStrategy
      attr_reader :num_workers, :total_records

      def initialize(num_workers, total_records)
        raise PartitionError, "Workers must be > 0" if num_workers <= 0
        @num_workers = num_workers
        @total_records = total_records
      end

      # Evenly distributes records across available TensorFlow workers
      def calculate_even_partitions
        records_per_worker = @total_records / @num_workers
        remainder = @total_records % @num_workers

        partitions = []
        start_idx = 0

        @num_workers.times do |i|
          # Distribute the remainder across the first few partitions
          chunk_size = records_per_worker + (i < remainder ? 1 : 0)
          
          partitions << {
            worker_id: i,
            start: start_idx,
            end: start_idx + chunk_size - 1,
            size: chunk_size
          }
          
          start_idx += chunk_size
        end

        partitions
      end

      # Validates that a Spark RDD partition mapping matches the required TF cluster size
      def validate_rdd_partitions(rdd_partition_count)
        if rdd_partition_count < @num_workers
          raise PartitionError, "RDD partitions (#{rdd_partition_count}) cannot be fewer than TF workers (#{@num_workers}). "\
                                "This will lead to idle GPUs."
        end
        true
      end
    end
  end
end

# Usage:
# strategy = Omni::TFSpark::PartitionStrategy.new(4, 10000)
# p strategy.calculate_even_partitions
