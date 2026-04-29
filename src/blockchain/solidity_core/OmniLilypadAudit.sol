// Omni Lilypad Prompt Audit Contract (Solidity)
// Ref: Mirascope/lilypad
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract OmniLilypadAudit {
    struct PromptVersion {
        bytes32 hash;
        address creator;
        uint256 timestamp;
        string templateUri;
    }

    mapping(bytes32 => PromptVersion) public versions;
    event VersionRegistered(bytes32 indexed hash, address creator, uint256 timestamp);

    function registerVersion(bytes32 _hash, string calldata _templateUri) external {
        require(versions[_hash].timestamp == 0, "Version already exists");
        versions[_hash] = PromptVersion(_hash, msg.sender, block.timestamp, _templateUri);
        emit VersionRegistered(_hash, msg.sender, block.timestamp);
    }

    function verifyVersion(bytes32 _hash) external view returns (bool exists, address creator, uint256 timestamp) {
        PromptVersion memory v = versions[_hash];
        return (v.timestamp > 0, v.creator, v.timestamp);
    }
}
