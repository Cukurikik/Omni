// SPDX-License-Identifier: OMNI-Open
// OMNI Divine Memory Integration: Inspired by Petals
// System Layer - Solidity Smart Contract for Distributed Node Registration

pragma solidity ^0.8.19;

contract PetalsNodeRegistry {
    uint256 public constant MAX_NODES = 10000;
    
    struct Node {
        address wallet;
        uint256 vram_offered_gb;
        bool is_active;
    }
    
    mapping(bytes32 => Node) public nodes;
    uint256 public activeNodeCount;

    event NodeRegistered(bytes32 indexed nodeId, uint256 vram);
    event NodeDeregistered(bytes32 indexed nodeId);

    error OmniError(uint256 code, string message);

    function registerNode(bytes32 nodeId, uint256 vram_gb) external {
        if (activeNodeCount >= MAX_NODES) {
            revert OmniError(413, "Maximum physical node registry capacity reached.");
        }
        
        if (vram_gb == 0 || vram_gb > 512) {
            revert OmniError(400, "VRAM bounds invalid (1-512GB).");
        }

        if (nodes[nodeId].is_active) {
            revert OmniError(409, "Node already active.");
        }

        nodes[nodeId] = Node({
            wallet: msg.sender,
            vram_offered_gb: vram_gb,
            is_active: true
        });

        activeNodeCount++;
        emit NodeRegistered(nodeId, vram_gb);
    }
}
