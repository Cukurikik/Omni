// @omni-layer Blockchain | @omni-lang Move (Sui/Aptos) | @omni-batch 17
// @omni-description On-chain inference ledger: Move smart contract for
// decentralized AI model provenance and verifiable inference tracking.

module omni::inference_ledger {
    use std::string::String;
    use std::signer;
    use std::vector;
    use aptos_framework::timestamp;
    use aptos_framework::coin;

    /// Error codes
    const E_NOT_AUTHORIZED: u64 = 1;
    const E_MODEL_NOT_FOUND: u64 = 2;
    const E_QUOTA_EXCEEDED: u64 = 3;
    const E_ALREADY_REGISTERED: u64 = 4;

    struct ModelRecord has key, store {
        model_id: u64,
        name: String,
        architecture: String,
        parameter_count: u64,
        creator: address,
        registered_at: u64,
        inference_count: u64,
        total_revenue: u64,
        is_active: bool,
    }

    struct InferenceLog has store, drop {
        model_id: u64,
        user: address,
        timestamp: u64,
        fee: u64,
        input_hash: vector<u8>,
        output_hash: vector<u8>,
    }

    struct Registry has key {
        models: vector<ModelRecord>,
        inference_logs: vector<InferenceLog>,
        next_model_id: u64,
        total_inferences: u64,
    }

    public fun initialize(account: &signer) {
        move_to(account, Registry {
            models: vector::empty<ModelRecord>(),
            inference_logs: vector::empty<InferenceLog>(),
            next_model_id: 0,
            total_inferences: 0,
        });
    }

    public fun register_model(
        account: &signer,
        name: String,
        architecture: String,
        parameter_count: u64,
    ) acquires Registry {
        let registry = borrow_global_mut<Registry>(signer::address_of(account));
        let model_id = registry.next_model_id;

        let model = ModelRecord {
            model_id,
            name,
            architecture,
            parameter_count,
            creator: signer::address_of(account),
            registered_at: timestamp::now_seconds(),
            inference_count: 0,
            total_revenue: 0,
            is_active: true,
        };

        vector::push_back(&mut registry.models, model);
        registry.next_model_id = model_id + 1;
    }

    public fun record_inference(
        account: &signer,
        registry_addr: address,
        model_id: u64,
        fee: u64,
        input_hash: vector<u8>,
        output_hash: vector<u8>,
    ) acquires Registry {
        let registry = borrow_global_mut<Registry>(registry_addr);
        assert!(model_id < vector::length(&registry.models), E_MODEL_NOT_FOUND);

        let model = vector::borrow_mut(&mut registry.models, model_id);
        assert!(model.is_active, E_MODEL_NOT_FOUND);

        model.inference_count = model.inference_count + 1;
        model.total_revenue = model.total_revenue + fee;
        registry.total_inferences = registry.total_inferences + 1;

        let log = InferenceLog {
            model_id,
            user: signer::address_of(account),
            timestamp: timestamp::now_seconds(),
            fee,
            input_hash,
            output_hash,
        };
        vector::push_back(&mut registry.inference_logs, log);
    }

    public fun deactivate_model(
        account: &signer,
        model_id: u64,
    ) acquires Registry {
        let registry = borrow_global_mut<Registry>(signer::address_of(account));
        let model = vector::borrow_mut(&mut registry.models, model_id);
        assert!(model.creator == signer::address_of(account), E_NOT_AUTHORIZED);
        model.is_active = false;
    }

    public fun get_total_inferences(registry_addr: address): u64 acquires Registry {
        borrow_global<Registry>(registry_addr).total_inferences
    }
}
