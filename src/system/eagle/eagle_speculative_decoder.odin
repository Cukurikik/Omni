// OMNI System Layer: eagle_speculative_decoder.odin
// Implements speculative decoding tree generation for EAGLE LLM acceleration.
// Hardware limits: Max 64 tree nodes per speculation step.

package system

import "core:mem"

// Hardware Bounds
MAX_TREE_NODES :: 64
MAX_TOKEN_ID   :: 128000 // Llama-3 vocabulary bound

OmniError :: enum {
	None,
	TreeOverflow,
	InvalidTokenId,
}

SpeculationNode :: struct {
	token_id: u32,
	prob:     f32,
	parent:   i32, // -1 for root
}

EagleDecoder :: struct {
	nodes: [MAX_TREE_NODES]SpeculationNode,
	count: i32,
}

// Monadic initialization
init_eagle_decoder :: proc() -> (EagleDecoder, OmniError) {
	decoder := EagleDecoder {
		count = 0,
	}
	return decoder, .None
}

// Add a node bounded strictly by physical tree limits
add_speculation_node :: proc(decoder: ^EagleDecoder, token_id: u32, prob: f32, parent: i32) -> OmniError {
	if decoder.count >= MAX_TREE_NODES {
		return .TreeOverflow
	}
	if token_id >= MAX_TOKEN_ID {
		return .InvalidTokenId
	}

	decoder.nodes[decoder.count] = SpeculationNode {
		token_id = token_id,
		prob     = prob,
		parent   = parent,
	}
	decoder.count += 1
	return .None
}

// Reset tree for next inference step
reset_decoder :: proc(decoder: ^EagleDecoder) {
	decoder.count = 0
}
