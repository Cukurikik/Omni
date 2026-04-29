module Omni
  module Business
    module SmartContractFuzzer
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

      class ReentrancyRules
        def check_reentrancy_risk(has_external_call, state_updated_after_call)
          # Smart Contract Security Business Logic: Reentrancy (The DAO hack)
          # If a contract makes an external call to an untrusted contract, and THEN updates its internal state (like balances),
          # the untrusted contract can call back into the original contract and drain funds before the state is updated.
          
          if has_external_call && state_updated_after_call
             return OmniResult.new(value: { 
               safe: false, 
               reason: "CRITICAL VULNERABILITY: Checks-Effects-Interactions pattern violated. Reentrancy possible." 
             })
          end
          
          OmniResult.new(value: { safe: true, reason: "Checks-Effects-Interactions pattern respected." })
        end
      end
    end
  end
end
