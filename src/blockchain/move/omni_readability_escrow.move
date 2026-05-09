// OMNI Framework - Move Smart Contract for Readability Escrow
// Decentralized escrow for rewarding agents that compute CommonLit readability scores.

module Omni::ReadabilityEscrow {
    use std::signer;
    use aptos_framework::coin;
    use aptos_framework::aptos_coin::AptosCoin;

    struct Escrow has key {
        balance: coin::Coin<AptosCoin>,
        requester: address,
    }

    public entry fun create_escrow(account: &signer, amount: u64) {
        let requester_addr = signer::address_of(account);
        let coins = coin::withdraw<AptosCoin>(account, amount);
        
        move_to(account, Escrow {
            balance: coins,
            requester: requester_addr,
        });
    }

    public entry fun release_funds(account: &signer, agent_address: address) acquires Escrow {
        let requester_addr = signer::address_of(account);
        let escrow = borrow_global_mut<Escrow>(requester_addr);
        
        // Extract funds from escrow and deposit to agent
        let reward = coin::extract_all(&mut escrow.balance);
        coin::deposit<AptosCoin>(agent_address, reward);
    }
}
