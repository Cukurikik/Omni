# OMNI Framework - AI Gig Escrow Contract (Vyper)
# Smart contract to hold funds until an AI model training task is cryptographically verified

# @version ^0.3.7

contract_owner: public(address)
worker: public(address)
amount: public(uint256)
is_completed: public(bool)

@external
@payable
def __init__(_worker: address):
    self.contract_owner = msg.sender
    self.worker = _worker
    self.amount = msg.value
    self.is_completed = False

@external
def submit_proof_and_claim(proof_hash: bytes32):
    """
    Worker calls this when training is done. 
    In a full implementation, a ZK-proof or oracle validates `proof_hash`.
    """
    assert msg.sender == self.worker, "OMNI: Only worker can claim"
    assert not self.is_completed, "OMNI: Job already completed"
    assert self.amount > 0, "OMNI: No funds in escrow"

    # Assume proof is verified off-chain or via Oracle
    self.is_completed = True
    
    send(self.worker, self.amount)

@external
def refund():
    """
    Owner can refund if the deadline passes (simplified).
    """
    assert msg.sender == self.contract_owner, "OMNI: Only owner can refund"
    assert not self.is_completed, "OMNI: Job already completed"
    
    self.is_completed = True
    send(self.contract_owner, self.amount)
