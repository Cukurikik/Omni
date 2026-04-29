// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// libp2p Kademlia DHT (OMNI Zero-Mock Implementation)
// Implements strict XOR metric distance calculation for exact routing geometries.

package compute

import (
	"errors"
)

type DistanceResult struct {
	Value []byte
	Error error
}

func OkDistanceResult(val []byte) DistanceResult {
	return DistanceResult{Value: val, Error: nil}
}

func ErrDistanceResult(err string) DistanceResult {
	return DistanceResult{Value: nil, Error: errors.New(err)}
}

// Performs mathematical structural XOR between peer ID cryptographic bounds
func CalculateKademliaXORDistance(nodeID1 []byte, nodeID2 []byte) DistanceResult {
	if len(nodeID1) == 0 || len(nodeID2) == 0 {
		return ErrDistanceResult("Node bounds logically undefined mathematically empty arrays.")
	}

	if len(nodeID1) != len(nodeID2) {
		return ErrDistanceResult("Kademlia algebraic constraints assert strictly identical byte lengths.")
	}

	distance := make([]byte, len(nodeID1))

	// Geometrically compute XOR distance representing exact DHT overlay topology pathing
	for i := 0; i < len(nodeID1); i++ {
		distance[i] = nodeID1[i] ^ nodeID2[i]
	}

	return OkDistanceResult(distance)
}
