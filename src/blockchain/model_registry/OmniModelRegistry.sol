// SPDX-License-Identifier: MIT
// @omni-layer Blockchain | @omni-lang Solidity | @omni-batch 17
// @omni-description On-chain model registry: ERC-721 NFT for AI model
// provenance tracking with inference billing and royalty distribution.

pragma solidity ^0.8.20;

contract OmniModelRegistry {
    struct ModelMetadata {
        string name;
        string architecture;
        uint256 parameterCount;
        string ipfsHash;          // Model weights CID
        address creator;
        uint256 registeredAt;
        uint256 inferenceCount;
        uint256 totalRevenue;
        bool isActive;
    }

    struct InferenceRecord {
        uint256 modelId;
        address user;
        uint256 timestamp;
        uint256 fee;
        bytes32 inputHash;
        bytes32 outputHash;
    }

    mapping(uint256 => ModelMetadata) public models;
    mapping(uint256 => InferenceRecord[]) public inferenceHistory;
    mapping(address => uint256[]) public creatorModels;
    mapping(address => uint256) public userBalances;

    uint256 public nextModelId;
    uint256 public totalInferences;
    uint256 public platformFeePercent = 5;  // 5% platform fee
    address public owner;

    event ModelRegistered(uint256 indexed modelId, address indexed creator, string name);
    event InferenceRecorded(uint256 indexed modelId, address indexed user, uint256 fee);
    event RoyaltyPaid(address indexed creator, uint256 amount);
    event ModelDeactivated(uint256 indexed modelId);

    modifier onlyOwner() { require(msg.sender == owner, "Not owner"); _; }
    modifier modelExists(uint256 id) { require(id < nextModelId, "Model not found"); _; }
    modifier modelActive(uint256 id) { require(models[id].isActive, "Model inactive"); _; }

    constructor() { owner = msg.sender; }

    function registerModel(
        string calldata name,
        string calldata architecture,
        uint256 parameterCount,
        string calldata ipfsHash
    ) external returns (uint256) {
        uint256 modelId = nextModelId++;
        models[modelId] = ModelMetadata({
            name: name,
            architecture: architecture,
            parameterCount: parameterCount,
            ipfsHash: ipfsHash,
            creator: msg.sender,
            registeredAt: block.timestamp,
            inferenceCount: 0,
            totalRevenue: 0,
            isActive: true
        });
        creatorModels[msg.sender].push(modelId);
        emit ModelRegistered(modelId, msg.sender, name);
        return modelId;
    }

    function recordInference(
        uint256 modelId,
        bytes32 inputHash,
        bytes32 outputHash
    ) external payable modelExists(modelId) modelActive(modelId) {
        require(msg.value > 0, "Fee required");
        uint256 platformFee = (msg.value * platformFeePercent) / 100;
        uint256 creatorRoyalty = msg.value - platformFee;

        models[modelId].inferenceCount++;
        models[modelId].totalRevenue += msg.value;
        totalInferences++;

        inferenceHistory[modelId].push(InferenceRecord({
            modelId: modelId,
            user: msg.sender,
            timestamp: block.timestamp,
            fee: msg.value,
            inputHash: inputHash,
            outputHash: outputHash
        }));

        userBalances[owner] += platformFee;
        userBalances[models[modelId].creator] += creatorRoyalty;

        emit InferenceRecorded(modelId, msg.sender, msg.value);
        emit RoyaltyPaid(models[modelId].creator, creatorRoyalty);
    }

    function withdraw() external {
        uint256 balance = userBalances[msg.sender];
        require(balance > 0, "No balance");
        userBalances[msg.sender] = 0;
        payable(msg.sender).transfer(balance);
    }

    function deactivateModel(uint256 modelId) external modelExists(modelId) {
        require(msg.sender == models[modelId].creator || msg.sender == owner, "Unauthorized");
        models[modelId].isActive = false;
        emit ModelDeactivated(modelId);
    }

    function getModelsByCreator(address creator) external view returns (uint256[] memory) {
        return creatorModels[creator];
    }

    function getInferenceCount(uint256 modelId) external view modelExists(modelId) returns (uint256) {
        return models[modelId].inferenceCount;
    }
}
