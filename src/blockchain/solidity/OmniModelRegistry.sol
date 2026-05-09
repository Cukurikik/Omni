// SPDX-License-Identifier: MIT
// OMNI Blockchain Layer — Solidity Smart Contract for Model NFT Registry
// On-chain model provenance, licensing, and inference payment.

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract OmniModelRegistry is ERC721, Ownable, ReentrancyGuard {

    struct ModelMetadata {
        string name;
        string version;
        string architecture;
        string ipfsHash;          // Model weights IPFS CID
        uint256 parameterCount;
        uint256 pricePerInference; // In wei
        address creator;
        uint256 totalInferences;
        bool isActive;
        uint256 createdAt;
    }

    uint256 private _nextTokenId;
    mapping(uint256 => ModelMetadata) public models;
    mapping(address => uint256) public creatorEarnings;
    mapping(address => mapping(uint256 => bool)) public accessGrants;

    uint256 public platformFeePercent = 5; // 5% platform fee
    uint256 public constant MAX_FEE = 20;

    event ModelRegistered(uint256 indexed tokenId, string name, address creator);
    event InferenceExecuted(uint256 indexed tokenId, address user, uint256 payment);
    event AccessGranted(uint256 indexed tokenId, address user);
    event EarningsWithdrawn(address creator, uint256 amount);

    constructor() ERC721("OmniModel", "OMODEL") Ownable(msg.sender) {}

    /// Register a new model as NFT
    function registerModel(
        string calldata name,
        string calldata version,
        string calldata architecture,
        string calldata ipfsHash,
        uint256 parameterCount,
        uint256 pricePerInference
    ) external returns (uint256) {
        require(bytes(name).length > 0, "Name required");
        require(bytes(ipfsHash).length > 0, "IPFS hash required");

        uint256 tokenId = _nextTokenId++;
        _safeMint(msg.sender, tokenId);

        models[tokenId] = ModelMetadata({
            name: name,
            version: version,
            architecture: architecture,
            ipfsHash: ipfsHash,
            parameterCount: parameterCount,
            pricePerInference: pricePerInference,
            creator: msg.sender,
            totalInferences: 0,
            isActive: true,
            createdAt: block.timestamp
        });

        emit ModelRegistered(tokenId, name, msg.sender);
        return tokenId;
    }

    /// Pay for inference execution
    function executeInference(uint256 tokenId) external payable nonReentrant {
        ModelMetadata storage model = models[tokenId];
        require(model.isActive, "Model not active");
        require(msg.value >= model.pricePerInference, "Insufficient payment");

        uint256 platformFee = (msg.value * platformFeePercent) / 100;
        uint256 creatorPayment = msg.value - platformFee;

        creatorEarnings[model.creator] += creatorPayment;
        model.totalInferences++;

        emit InferenceExecuted(tokenId, msg.sender, msg.value);
    }

    /// Grant access to a model
    function grantAccess(uint256 tokenId, address user) external {
        require(ownerOf(tokenId) == msg.sender, "Not model owner");
        accessGrants[user][tokenId] = true;
        emit AccessGranted(tokenId, user);
    }

    /// Withdraw creator earnings
    function withdrawEarnings() external nonReentrant {
        uint256 amount = creatorEarnings[msg.sender];
        require(amount > 0, "No earnings");
        creatorEarnings[msg.sender] = 0;
        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "Transfer failed");
        emit EarningsWithdrawn(msg.sender, amount);
    }

    /// Deactivate a model
    function deactivateModel(uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender, "Not model owner");
        models[tokenId].isActive = false;
    }

    /// Update platform fee (owner only)
    function setPlatformFee(uint256 newFee) external onlyOwner {
        require(newFee <= MAX_FEE, "Fee too high");
        platformFeePercent = newFee;
    }

    function hasAccess(address user, uint256 tokenId) external view returns (bool) {
        return ownerOf(tokenId) == user || accessGrants[user][tokenId];
    }
}
