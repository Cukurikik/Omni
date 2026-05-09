// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title OmniSmartContract
 * @dev On-chain registry for AI models within the OMNI Ecosystem
 */
contract OmniSmartContract {
    struct AIModel {
        string name;
        string ipfsHash;
        address owner;
        uint256 createdAt;
        bool isActive;
    }

    mapping(bytes32 => AIModel) public models;
    event ModelRegistered(bytes32 indexed modelId, string name, address indexed owner);

    function registerModel(bytes32 modelId, string memory name, string memory ipfsHash) public {
        require(models[modelId].owner == address(0), "Model already exists");
        
        models[modelId] = AIModel({
            name: name,
            ipfsHash: ipfsHash,
            owner: msg.sender,
            createdAt: block.timestamp,
            isActive: true
        });

        emit ModelRegistered(modelId, name, msg.sender);
    }

    function deactivateModel(bytes32 modelId) public {
        require(models[modelId].owner == msg.sender, "Only owner can deactivate");
        models[modelId].isActive = false;
    }
}
