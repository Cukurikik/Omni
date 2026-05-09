# moe_ruby_dsl_router.rb — Domain / Configuration
# Layer: Domain / Config — Declarative Routing DSL
#
# Hardcoding MoE routing rules inside the core C++ or Python code makes the system
# rigid. This Ruby script implements a Domain-Specific Language (DSL) that allows
# system administrators to declaratively define how tokens and topics map to Experts.

class MoeRouterDSL
    def initialize
        @routing_rules = []
        puts "[Ruby DSL] Initialized Declarative MoE Routing Engine."
    end
    
    # Defines a routing rule mapping a Regex topic to an Expert ID
    def route(topic_pattern, to_expert:, confidence_boost: 0.0)
        @routing_rules << {
            pattern: topic_pattern,
            expert_id: to_expert,
            boost: confidence_boost
        }
        puts "[Ruby DSL] Added rule: #{topic_pattern.inspect} -> Expert #{to_expert}"
    end
    
    # Sets up a fallback expert if no rules match and the neural router is unsure
    def default_fallback(expert_id)
        @fallback = expert_id
        puts "[Ruby DSL] Fallback Expert set to #{expert_id}"
    end
    
    # Evaluates an incoming prompt against the rules
    def evaluate(prompt_text)
        @routing_rules.each do |rule|
            if prompt_text.match?(rule[:pattern])
                return {
                    matched: true,
                    expert_id: rule[:expert_id],
                    boost: rule[:boost]
                }
            end
        end
        
        return {
            matched: false,
            expert_id: @fallback || 0,
            boost: 0.0
        }
    end
end

# --- DSL Usage Example ---
# This file would be loaded dynamically at runtime by the Orchestrator

router = MoeRouterDSL.new

# Route coding queries to Expert 1 (Code)
router.route /function|class|def|void|return/i, to_expert: 1, confidence_boost: 2.5

# Route medical queries to Expert 2 (Medical)
router.route /symptom|pain|doctor|fever/i, to_expert: 2, confidence_boost: 2.0

# Route anime queries to Expert 12 (Anime)
router.route /anime|manga|shounen|isekai/i, to_expert: 12, confidence_boost: 3.0

router.default_fallback 0 # Expert 0 is General Knowledge
