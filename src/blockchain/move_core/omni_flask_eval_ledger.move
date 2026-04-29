module Omni::FlaskEvalLedger {

    // Omni FLASK Eval Ledger (Move)
    // Deterministic logging of model evaluation metrics on-chain.

    use std::signer;

    struct EvaluationRecord has store, key {
        alignment_score: u64, // Scaled by 10000
    }

    const ERR_INVALID_SCORE: u64 = 1;

    public fun record_evaluation(account: &signer, score: u64) {
        assert!(score <= 10000, ERR_INVALID_SCORE);
        
        let account_addr = signer::address_of(account);
        
        // Deterministic state mutation
        move_to(account, EvaluationRecord { alignment_score: score });
    }
}
