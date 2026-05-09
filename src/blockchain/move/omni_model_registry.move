// OMNI Blockchain Layer — Move Smart Contract for Model Registry (Sui/Aptos)
// On-chain model provenance with Move's ownership model.

module omni::model_registry {
    use std::string::{Self, String};
    use std::vector;
    use sui::object::{Self, UID};
    use sui::transfer;
    use sui::tx_context::{Self, TxContext};
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;
    use sui::event;

    /// Model NFT representing a registered AI model
    struct ModelNFT has key, store {
        id: UID,
        name: String,
        version: String,
        architecture: String,
        ipfs_hash: String,
        parameter_count: u64,
        price_per_inference: u64,
        creator: address,
        total_inferences: u64,
        is_active: bool,
    }

    /// Registry for tracking all models
    struct ModelRegistry has key {
        id: UID,
        total_models: u64,
        platform_fee_bps: u64, // Basis points (100 = 1%)
        admin: address,
    }

    /// Events
    struct ModelRegistered has copy, drop {
        model_id: address,
        name: String,
        creator: address,
    }

    struct InferenceExecuted has copy, drop {
        model_id: address,
        user: address,
        payment: u64,
    }

    /// Initialize the registry
    fun init(ctx: &mut TxContext) {
        let registry = ModelRegistry {
            id: object::new(ctx),
            total_models: 0,
            platform_fee_bps: 500, // 5%
            admin: tx_context::sender(ctx),
        };
        transfer::share_object(registry);
    }

    /// Register a new model as NFT
    public entry fun register_model(
        registry: &mut ModelRegistry,
        name: vector<u8>,
        version: vector<u8>,
        architecture: vector<u8>,
        ipfs_hash: vector<u8>,
        parameter_count: u64,
        price_per_inference: u64,
        ctx: &mut TxContext,
    ) {
        let model = ModelNFT {
            id: object::new(ctx),
            name: string::utf8(name),
            version: string::utf8(version),
            architecture: string::utf8(architecture),
            ipfs_hash: string::utf8(ipfs_hash),
            parameter_count,
            price_per_inference,
            creator: tx_context::sender(ctx),
            total_inferences: 0,
            is_active: true,
        };

        event::emit(ModelRegistered {
            model_id: object::uid_to_address(&model.id),
            name: model.name,
            creator: model.creator,
        });

        registry.total_models = registry.total_models + 1;
        transfer::transfer(model, tx_context::sender(ctx));
    }

    /// Execute inference (pay model creator)
    public entry fun execute_inference(
        model: &mut ModelNFT,
        payment: Coin<SUI>,
        ctx: &mut TxContext,
    ) {
        assert!(model.is_active, 0);
        assert!(coin::value(&payment) >= model.price_per_inference, 1);

        model.total_inferences = model.total_inferences + 1;

        event::emit(InferenceExecuted {
            model_id: object::uid_to_address(&model.id),
            user: tx_context::sender(ctx),
            payment: coin::value(&payment),
        });

        transfer::public_transfer(payment, model.creator);
    }

    /// Deactivate model
    public entry fun deactivate_model(model: &mut ModelNFT, ctx: &TxContext) {
        assert!(model.creator == tx_context::sender(ctx), 2);
        model.is_active = false;
    }

    /// View functions
    public fun get_model_name(model: &ModelNFT): &String { &model.name }
    public fun get_total_inferences(model: &ModelNFT): u64 { model.total_inferences }
    public fun is_active(model: &ModelNFT): bool { model.is_active }
}
