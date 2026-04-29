// Omni ETO Agent Credits (Move)
// Contract Layer: On-chain credit for trajectory optimization runs.
// Ref: Yifan-Song793/ETO

module omni::eto_credits {
    use std::signer;
    struct Credits has key { balance: u64 }
    const ERR_INSUFFICIENT: u64 = 1;

    public fun init(account: &signer) {
        move_to(account, Credits { balance: 100 });
    }

    public fun deduct(account: &signer, amount: u64) acquires Credits {
        let addr = signer::address_of(account);
        let c = borrow_global_mut<Credits>(addr);
        assert!(c.balance >= amount, ERR_INSUFFICIENT);
        c.balance = c.balance - amount;
    }
}
