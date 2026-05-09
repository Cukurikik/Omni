module OmniEcosystem::ModelComputeRewards {
    use std::signer;
    use aptos_framework::coin;
    use aptos_framework::aptos_coin::AptosCoin;

    /// Omni Move Smart Contract (Blockchain Layer)
    /// Decentralized reward distribution for nodes contributing compute power
    /// to the OMNI Transformer training clusters.

    struct ComputeRegistry has key {
        total_flops_contributed: u64,
        reward_pool: coin::Coin<AptosCoin>,
    }

    struct NodeStats has key {
        flops_contributed: u64,
        models_trained: u64,
    }

    const E_NOT_AUTHORIZED: u64 = 1;
    const E_INSUFFICIENT_POOL: u64 = 2;

    public entry fun initialize_registry(admin: &signer, initial_funding: u64) {
        // Ensure only Omni admin can initialize
        assert!(signer::address_of(admin) == @OmniEcosystem, E_NOT_AUTHORIZED);

        let coins = coin::withdraw<AptosCoin>(admin, initial_funding);
        move_to(admin, ComputeRegistry {
            total_flops_contributed: 0,
            reward_pool: coins,
        });
    }

    public entry fun register_node(node: &signer) {
        if (!exists<NodeStats>(signer::address_of(node))) {
            move_to(node, NodeStats {
                flops_contributed: 0,
                models_trained: 0,
            });
        }
    }

    public entry fun log_compute_and_reward(
        admin: &signer, 
        node_addr: address, 
        flops: u64, 
        reward_amount: u64
    ) acquires ComputeRegistry, NodeStats {
        assert!(signer::address_of(admin) == @OmniEcosystem, E_NOT_AUTHORIZED);
        
        // Update Node Stats
        let node_stats = borrow_global_mut<NodeStats>(node_addr);
        node_stats.flops_contributed = node_stats.flops_contributed + flops;
        node_stats.models_trained = node_stats.models_trained + 1;

        // Update Global Registry
        let registry = borrow_global_mut<ComputeRegistry>(@OmniEcosystem);
        registry.total_flops_contributed = registry.total_flops_contributed + flops;

        // Distribute Reward
        assert!(coin::value(&registry.reward_pool) >= reward_amount, E_INSUFFICIENT_POOL);
        let reward_coins = coin::extract(&mut registry.reward_pool, reward_amount);
        coin::deposit(node_addr, reward_coins);
    }
}
