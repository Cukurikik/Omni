module Omni
  module Compute
    # OMNI MOTHER Production Zero-Mock Architecture Matrix Generator
    # Dynamically generates living comparison tables of LLM architectures
    # Outputting HTML or Markdown matrices.

    class ArchTableGenerator
      def initialize
        @models = []
      end

      def add_model(name, year, norm, attention, moe, positional)
        @models << {
          name: name,
          year: year,
          norm: norm,
          attention: attention,
          moe: moe,
          positional: positional
        }
      end

      def generate_markdown
        md = []
        md << "| Model | Year | Normalization | Attention | MoE Type | Positional Encoding |"
        md << "|---|---|---|---|---|---|"
        
        @models.sort_by { |m| m[:year] }.each do |m|
          md << "| #{m[:name]} | #{m[:year]} | #{m[:norm]} | #{m[:attention]} | #{m[:moe]} | #{m[:positional]} |"
        end
        
        md.join("\n")
      end
    end
  end
end

# Usage:
# table = Omni::Compute::ArchTableGenerator.new
# table.add_model("Transformer", 2017, "Post-LN", "MHA", "None", "Absolute Sinusoidal")
# table.add_model("Mixtral 8x7B", 2023, "RMSNorm", "GQA", "Sparse Top-2", "RoPE")
# puts table.generate_markdown
