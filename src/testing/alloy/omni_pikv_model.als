// OMNI MOTHER: Alloy Analyzer (TLA+ Alternative)
// Validates PiKV cache block allocation state

module OmniPiKVModel

sig Block {}
sig Request {
    allocates: set Block
}

fact UniqueAllocation {
    // A block cannot be allocated to two different requests
    all b: Block | lone r: Request | b in r.allocates
}

pred show {}
run show for 3 Request, 5 Block
