// @omni-layer Blockchain | @omni-lang Move | @omni-batch 18 | @omni-semester 16
// @omni-description Move module for transformer model marketplace on Aptos/Sui.
module omni::transformer_marketplace {
    use std::string::String;
    use std::signer;
    use aptos_framework::coin;
    use aptos_framework::timestamp;

    struct ModelInfo has key, store, copy, drop {
        model_id: String,
        model_type: String,
        version: String,
        params_million: u64,
        inference_price: u64,
        total_inferences: u64,
        active: bool,
        created_at: u64,
    }

    struct ModelRegistry has key {
        models: vector<ModelInfo>,
        admin: address,
        total_revenue: u64,
    }

    struct UserCredits has key {
        balance: u64,
        total_spent: u64,
    }

    const E_NOT_ADMIN: u64 = 1;
    const E_MODEL_NOT_FOUND: u64 = 2;
    const E_INSUFFICIENT_CREDITS: u64 = 3;
    const E_MODEL_INACTIVE: u64 = 4;

    public entry fun initialize(admin: &signer) {
        let registry = ModelRegistry {
            models: vector::empty<ModelInfo>(),
            admin: signer::address_of(admin),
            total_revenue: 0,
        };
        move_to(admin, registry);
    }

    public entry fun register_model(
        owner: &signer,
        model_id: String,
        model_type: String,
        version: String,
        params_million: u64,
        inference_price: u64,
    ) acquires ModelRegistry {
        let registry = borrow_global_mut<ModelRegistry>(@omni);
        let model = ModelInfo {
            model_id,
            model_type,
            version,
            params_million,
            inference_price,
            total_inferences: 0,
            active: true,
            created_at: timestamp::now_seconds(),
        };
        vector::push_back(&mut registry.models, model);
    }

    public entry fun deposit_credits(user: &signer, amount: u64) acquires UserCredits {
        let addr = signer::address_of(user);
        if (!exists<UserCredits>(addr)) {
            move_to(user, UserCredits { balance: amount, total_spent: 0 });
        } else {
            let credits = borrow_global_mut<UserCredits>(addr);
            credits.balance = credits.balance + amount;
        };
    }

    public entry fun execute_inference(
        user: &signer,
        model_index: u64,
    ) acquires ModelRegistry, UserCredits {
        let addr = signer::address_of(user);
        let registry = borrow_global_mut<ModelRegistry>(@omni);
        let model = vector::borrow_mut(&mut registry.models, model_index);

        assert!(model.active, E_MODEL_INACTIVE);

        let credits = borrow_global_mut<UserCredits>(addr);
        assert!(credits.balance >= model.inference_price, E_INSUFFICIENT_CREDITS);

        credits.balance = credits.balance - model.inference_price;
        credits.total_spent = credits.total_spent + model.inference_price;
        model.total_inferences = model.total_inferences + 1;
        registry.total_revenue = registry.total_revenue + model.inference_price;
    }
}
