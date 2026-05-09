// OMNI MOTHER: Alloy Analyzer
// Validates Gateway Routing logic

module OmniGatewayModel

sig Node {}
sig Request {
    routedTo: lone Node
}

fact AllRequestsRouted {
    all r: Request | some r.routedTo
}

pred show {}
run show for 3 Request, 2 Node
