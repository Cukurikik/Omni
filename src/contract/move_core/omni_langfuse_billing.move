// Omni Langfuse Billing (Move)
// Smart Contract Layer: On-chain settlement for API telemetry usage.

module omni::langfuse_billing {
    use std::signer;

    struct BillingState has key {
        trace_count: u64,
        total_cost_omni: u64,
    }

    const ERR_NOT_INITIALIZED: u64 = 1;
    const OMNI_COST_PER_TRACE: u64 = 15;

    public fun initialize(account: &signer) {
        move_to(account, BillingState {
            trace_count: 0,
            total_cost_omni: 0,
        });
    }

    public fun record_trace(account: &signer) acquires BillingState {
        let addr = signer::address_of(account);
        assert!(exists<BillingState>(addr), ERR_NOT_INITIALIZED);

        let state = borrow_global_mut<BillingState>(addr);
        state.trace_count = state.trace_count + 1;
        state.total_cost_omni = state.total_cost_omni + OMNI_COST_PER_TRACE;
    }
}
