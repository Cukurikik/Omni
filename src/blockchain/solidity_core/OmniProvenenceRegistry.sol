// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title Omni Provenance Registry
 * @dev Strict production-grade Solidity smart contract for the Omni Blockchain Layer.
 * Enforces Zero-Mock logic and custom error handling.
 */
contract OmniProvenanceRegistry {
    
    error InvalidHash();
    error AssetAlreadyRegistered();

    struct Asset {
        bytes32 dataHash;
        uint256 timestamp;
        address owner;
    }

    mapping(bytes32 => Asset) public registry;

    function registerAsset(bytes32 _hash) external returns (bool) {
        if (_hash == bytes32(0)) revert InvalidHash();
        if (registry[_hash].timestamp != 0) revert AssetAlreadyRegistered();

        registry[_hash] = Asset({
            dataHash: _hash,
            timestamp: block.timestamp,
            owner: msg.sender
        });

        return true; // Monadic-style success indicator
    }
}
