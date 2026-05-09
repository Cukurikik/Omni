# moe_llm_bench_aggregator.rb — Domain Layer: LLM Bench Aggregator
# Ruby business logic for aggregating and ranking cross-platform hardware benchmarks.

module Omni
  module MoE
    module LLMBench
      class BenchAggregator
        def initialize
          @results = []
        end

        def add_result(hardware_name, tokens_per_second, memory_used_mb)
          raise ArgumentError, "Invalid metric" if tokens_per_second <= 0
          
          @results << {
            hardware: hardware_name,
            tps: tokens_per_second,
            mem: memory_used_mb,
            efficiency: tokens_per_second / memory_used_mb.to_f
          }
        end

        def get_ranked_hardware
          # Ranks hardware by inference efficiency (TPS per MB of VRAM)
          @results.sort_by { |res| -res[:efficiency] }
        end
        
        def calculate_global_average_tps
          return 0 if @results.empty?
          total_tps = @results.map { |r| r[:tps] }.sum
          total_tps / @results.size.to_f
        end
      end
    end
  end
end
