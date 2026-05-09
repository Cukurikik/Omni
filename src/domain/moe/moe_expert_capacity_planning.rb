# moe_expert_capacity_planning.rb — Domain / Infrastructure
# Layer: Domain / Operations — MoE VRAM Capacity Planner
#
# MoE clusters require exact hardware planning to avoid OOM errors.
# This Ruby script calculates the required VRAM and GPU count based on 
# expert size, quantization level, and projected active tokens per second.

class CapacityPlanner
  VRAM_PER_GPU_GB = 80.0 # Standard A100/H100

  def initialize(expert_count, param_billion_per_expert, quant_bits)
    @expert_count = expert_count
    @params_b = param_billion_per_expert
    @quant_bits = quant_bits
  end

  def calculate
    # 1 byte per parameter at 8-bit. 2 bytes at 16-bit.
    bytes_per_param = @quant_bits / 8.0
    
    gb_per_expert = @params_b * bytes_per_param
    total_weights_gb = gb_per_expert * @expert_count

    # KV Cache approximation (Assuming 8192 context, 1024 batch)
    kv_cache_overhead_gb = (@expert_count * 0.15) # Very rough heuristic

    total_required_vram = total_weights_gb + kv_cache_overhead_gb
    
    # 90% utilization safety margin
    gpus_required = (total_required_vram / (VRAM_PER_GPU_GB * 0.90)).ceil

    puts "========== MoE Capacity Planner =========="
    puts "Total Experts:      #{@expert_count}"
    puts "Params per Expert:  #{@params_b} Billion"
    puts "Quantization:       #{@quant_bits}-bit"
    puts "------------------------------------------"
    puts "Weight VRAM:        #{total_weights_gb.round(2)} GB"
    puts "KV Cache VRAM:      #{kv_cache_overhead_gb.round(2)} GB"
    puts "Total Req VRAM:     #{total_required_vram.round(2)} GB"
    puts "=> Minimum GPUs (80GB) Required: #{gpus_required}"
    puts "=========================================="
  end
end

# Usage if executed directly
if __FILE__ == $0
  # Example: 16 experts, 7 Billion params each, 4-bit (AWQ) quantization
  planner = CapacityPlanner.new(16, 7.0, 4)
  planner.calculate
end
