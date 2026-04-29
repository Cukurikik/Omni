module Omni
  module Business
    module DocumentLayoutAnalyzer
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

      class ReadingOrderRules
        def determine_order(blocks)
          if blocks.nil? || blocks.empty?
            return OmniResult.new(error: StandardError.new("Document blocks cannot be empty"))
          end

          # Layout Business Logic: Reading Order Sorting
          # Sorts physical PDF text blocks into logical reading order (Top-to-Bottom, Left-to-Right)
          # Critical for preserving context in RAG document chunks
          
          sorted_blocks = blocks.sort do |a, b|
             # Assume blocks have { y: top_y, x: left_x }
             # Sort primarily by Y (vertical), with a tolerance for inline text, then by X (horizontal)
             
             y_diff = (a[:y] - b[:y]).abs
             if y_diff < 10.0 # Same line tolerance
               a[:x] <=> b[:x]
             else
               a[:y] <=> b[:y]
             end
          end
          
          OmniResult.new(value: sorted_blocks)
        end
      end
    end
  end
end
