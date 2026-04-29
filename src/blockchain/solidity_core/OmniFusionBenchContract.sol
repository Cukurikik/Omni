// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title Omni Fusion Bench Contract
 * @dev Strict production-grade Solidity smart contract for the Omni Blockchain Layer.
 * Evaluates model weight merging signatures on-chain.
 */
contract OmniFusionBenchContract {
    
    error InvalidSignature();
    error MergeAlreadyRecorded();

    struct MergeRecord {
        bytes32 modelA;
        bytes32 modelB;
        uint256 alpha; // Scaled by 1000
    }

    mapping(bytes32 => MergeRecord) public records;

    function recordMerge(bytes32 _modelA, bytes32 _modelB, uint256 _alpha) external returns (bool) {
        if (_modelA == bytes32(0) || _modelB == bytes32(0)) revert InvalidSignature();
        bytes32 mergeHash = keccak256(abi.encodePacked(_modelA, _modelB, _alpha));
        
        if (records[mergeHash].modelA != bytes32(0)) revert MergeAlreadyRecorded();

        records[mergeHash] = MergeRecord({
            modelA: _modelA,
            modelB: _modelB,
            alpha: _alpha
        });

        return true; // Monadic-style success indicator
    }
}
