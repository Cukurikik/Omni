# frozen_string_literal: true

# OMNI MOTHER: MoE Paper Configurations Registry (Production Grade)
# A comprehensive registry of known Mixture-of-Experts architectures based on literature.

module Omni
  module Models
    class MoeRegistry
      class << self
        def known_models
          @known_models ||= {
            'switch_transformer' => {
              authors: ['Fedus', 'Zoph', 'Shazeer'],
              year: 2021,
              routing: 'top-1',
              expert_capacity_factor: 1.0,
              loss_type: 'load_balancing',
              description: 'Scales models to trillions of parameters with simple top-1 routing.'
            },
            'gshard' => {
              authors: ['Lepikhin', 'et al.'],
              year: 2020,
              routing: 'top-2',
              expert_capacity_factor: 2.0,
              loss_type: 'auxiliary',
              description: 'Pioneered top-2 gating for translation tasks with massive scale.'
            },
            'mixtral_8x7b' => {
              authors: ['Mistral AI'],
              year: 2024,
              routing: 'top-2',
              num_experts: 8,
              active_experts: 2,
              hidden_dim: 4096,
              description: 'Open-weights sparse MoE outperforming dense models of similar active parameters.'
            },
            'qwen1.5_moe' => {
              authors: ['Alibaba Cloud'],
              year: 2024,
              routing: 'top-4',
              num_experts: 64, # Fine-grained experts
              active_experts: 4,
              description: 'Uses many smaller experts rather than a few large ones for better expressiveness.'
            },
            'deepseek_moe' => {
              authors: ['DeepSeek AI'],
              year: 2024,
              routing: 'top-k_with_shared',
              num_experts: 64,
              shared_experts: 2,
              description: 'Isolates general knowledge into shared experts to prevent redundancy.'
            },
            'demoe' => {
              authors: ['Omni Research'],
              year: 2026,
              routing: 'patch_wise',
              num_experts: 16,
              domain: 'image_deblurring',
              description: 'Allocates specific experts to different blur kernels/motion vectors in images.'
            }
          }.freeze
        end

        def get_model(name)
          known_models[name.downcase]
        end

        def active_parameters(name, base_params, expert_params)
          model = get_model(name)
          return nil unless model
          
          active = model[:active_experts] || 1
          base_params + (expert_params * active)
        end
        
        def find_by_routing(strategy)
          known_models.select { |_, config| config[:routing] == strategy }
        end
      end
    end
  end
end
