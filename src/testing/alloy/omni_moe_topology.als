// OMNI MOTHER: Alloy Analyzer for Network Topology

module OmniTopologyModel

sig Rack {}
sig Server {
    inRack: exact 1 Rack
}

fact ServerDistribution {
    // Ensure every rack has at least one server
    all r: Rack | some s: Server | s.inRack = r
}

pred show {}
run show for 4 Server, 2 Rack
