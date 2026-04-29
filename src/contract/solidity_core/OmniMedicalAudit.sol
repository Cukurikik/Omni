// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Omni Medical LLM Audit Registry (Solidity)
// Contract Layer: On-chain audit trail for medical inference.
// Ref: BIDS-Xu-Lab/Me-LLaMA

contract OmniMedicalAudit {
    struct InferenceRecord { uint256 timestamp; bytes32 promptHash; string model; }
    mapping(address => InferenceRecord[]) public records;
    event InferenceLogged(address indexed user, bytes32 promptHash);

    function logInference(bytes32 _hash, string calldata _model) external {
        records[msg.sender].push(InferenceRecord(block.timestamp, _hash, _model));
        emit InferenceLogged(msg.sender, _hash);
    }
}
