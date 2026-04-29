module Omni
  module Business
    module PromptML

      class OmniResult
        attr_reader :data, :error
        def initialize(data: nil, error: nil)
          @data = data
          @error = error
        end
        def ok?
          @error.nil?
        end
      end

      class ModelRegistry
        def initialize
          @registry = {}
        end

        def register_architecture(prompt, ast_payload)
          return OmniResult.new(error: "Invalid input") if prompt.nil? || ast_payload.nil? || ast_payload.empty?
          
          # Mathematical validation of model graph depth
          depth = ast_payload["layers"]&.length || 0
          if depth > 1000
            return OmniResult.new(error: "Architecture exceeds maximum allowable depth of 1000 layers.")
          end

          # Cryptographic hashing for model versioning
          hash_input = "#{prompt}-#{depth}-#{Time.now.to_i}"
          version_hash = Digest::SHA256.hexdigest(hash_input)[0..15]
          
          model_urn = "urn:omni:model:#{version_hash}"
          
          @registry[model_urn] = {
            prompt: prompt,
            depth: depth,
            status: "REGISTERED",
            created_at: Time.now.utc
          }

          OmniResult.new(data: { model_urn: model_urn, depth: depth })
        end

        def get_model(urn)
          if @registry.key?(urn)
            OmniResult.new(data: @registry[urn])
          else
            OmniResult.new(error: "Model not found: #{urn}")
          end
        end
      end

    end
  end
end
