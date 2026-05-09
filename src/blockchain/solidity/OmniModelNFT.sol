// SPDX-License-Identifier: MIT
// OMNI Blockchain — Solidity Model NFT Registry
// ERC-721 model ownership with on-chain inference credits.
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract OmniModelNFT is ERC721, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    struct ModelMetadata {
        string name;
        string version;
        string ipfsHash;      // Model weights on IPFS
        uint256 parameters;
        uint256 inferenceCredits;
        uint256 pricePerInference; // in wei
        bool isActive;
        uint256 totalInferences;
    }

    mapping(uint256 => ModelMetadata) public models;
    mapping(address => uint256[]) public ownerModels;
    mapping(uint256 => mapping(address => uint256)) public userCredits;

    event ModelRegistered(uint256 indexed tokenId, string name, address owner);
    event InferenceExecuted(uint256 indexed tokenId, address indexed user, uint256 creditsUsed);
    event CreditsPurchased(uint256 indexed tokenId, address indexed buyer, uint256 amount);

    constructor() ERC721("OMNI Model", "OMNI") Ownable(msg.sender) {}

    function registerModel(
        string memory name,
        string memory version,
        string memory ipfsHash,
        uint256 parameters,
        uint256 pricePerInference
    ) external returns (uint256) {
        _tokenIds.increment();
        uint256 tokenId = _tokenIds.current();
        _safeMint(msg.sender, tokenId);

        models[tokenId] = ModelMetadata({
            name: name,
            version: version,
            ipfsHash: ipfsHash,
            parameters: parameters,
            inferenceCredits: 0,
            pricePerInference: pricePerInference,
            isActive: true,
            totalInferences: 0
        });

        ownerModels[msg.sender].push(tokenId);
        emit ModelRegistered(tokenId, name, msg.sender);
        return tokenId;
    }

    function purchaseCredits(uint256 tokenId, uint256 amount) external payable {
        require(_ownerOf(tokenId) != address(0), "Model does not exist");
        require(models[tokenId].isActive, "Model is not active");
        require(msg.value >= models[tokenId].pricePerInference * amount, "Insufficient payment");

        userCredits[tokenId][msg.sender] += amount;
        payable(ownerOf(tokenId)).transfer(msg.value);
        emit CreditsPurchased(tokenId, msg.sender, amount);
    }

    function executeInference(uint256 tokenId) external {
        require(userCredits[tokenId][msg.sender] > 0, "No credits");
        require(models[tokenId].isActive, "Model inactive");

        userCredits[tokenId][msg.sender]--;
        models[tokenId].totalInferences++;
        emit InferenceExecuted(tokenId, msg.sender, 1);
    }

    function getModel(uint256 tokenId) external view returns (ModelMetadata memory) {
        return models[tokenId];
    }

    function totalModels() external view returns (uint256) {
        return _tokenIds.current();
    }
}
