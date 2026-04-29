module Omni
  module Business
    module PrReviewBot
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

      class ConflictResolution
        def can_auto_resolve(file_extension, conflict_type)
          if file_extension.nil? || conflict_type.nil?
            return OmniResult.new(error: StandardError.new("File extension and conflict type required"))
          end

          # PR Review Business Logic: Auto-Merge Safety
          # Determines if the AI PR bot is allowed to automatically resolve a git merge conflict
          
          # Never auto-resolve compiled binaries or lock files
          unsafe_extensions = [".lock", ".dll", ".so", ".bin"]
          if unsafe_extensions.include?(file_extension)
             return OmniResult.new(value: { can_resolve: false, reason: "Unsafe file type for auto-resolution" })
          end
          
          if conflict_type == "whitespace_only"
             return OmniResult.new(value: { can_resolve: true, reason: "Safe whitespace resolution" })
          end
          
          OmniResult.new(value: { can_resolve: false, reason: "Requires human manual review" })
        end
      end
    end
  end
end
