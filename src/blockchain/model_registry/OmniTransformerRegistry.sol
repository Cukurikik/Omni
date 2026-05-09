// SPDX-License-Identifier: MIT
// OmniTransformerRegistry.sol — On-Chain Model Registry
// Inspired by: Decentralized AI model governance
// Layer: Blockchain / Solidity
//
// Smart contract for registering, versioning, and verifying
// ML model checkpoints on-chain with hash-based integrity proofs.

pragma solidity ^0.8.20;

contract OmniTransformerRegistry {
    struct ModelVersion {
        uint256 versionId;
        string modelName;
        string artifactHash;      // SHA-256 hash of model weights
        string metadataURI;       // IPFS URI for model card
        uint256 parameterCount;
        string architecture;      // e.g., "conformer-12L-8H"
        address registrant;
        uint256 registeredAt;
        bool verified;
        uint256 verificationCount;
    }

    struct ModelEntry {
        string name;
        string description;
        address owner;
        uint256 latestVersion;
        uint256 createdAt;
        bool active;
    }

    mapping(string => ModelEntry) public models;
    mapping(string => mapping(uint256 => ModelVersion)) public versions;
    mapping(address => bool) public verifiers;
    mapping(string => mapping(uint256 => mapping(address => bool))) public hasVerified;

    string[] public modelNames;
    address public admin;
    uint256 public totalModels;
    uint256 public totalVersions;
    uint256 public verificationThreshold;

    event ModelRegistered(string indexed name, address indexed owner);
    event VersionPublished(string indexed name, uint256 versionId, string artifactHash);
    event ModelVerified(string indexed name, uint256 versionId, address verifier);
    event VerifierAdded(address indexed verifier);
    event VerifierRemoved(address indexed verifier);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin");
        _;
    }

    modifier onlyModelOwner(string memory name) {
        require(models[name].owner == msg.sender, "Not model owner");
        _;
    }

    modifier onlyVerifier() {
        require(verifiers[msg.sender], "Not a verifier");
        _;
    }

    constructor(uint256 _verificationThreshold) {
        admin = msg.sender;
        verificationThreshold = _verificationThreshold;
        verifiers[msg.sender] = true;
    }

    function registerModel(
        string memory name,
        string memory description
    ) external {
        require(bytes(models[name].name).length == 0, "Model already exists");

        models[name] = ModelEntry({
            name: name,
            description: description,
            owner: msg.sender,
            latestVersion: 0,
            createdAt: block.timestamp,
            active: true
        });

        modelNames.push(name);
        totalModels++;

        emit ModelRegistered(name, msg.sender);
    }

    function publishVersion(
        string memory name,
        string memory artifactHash,
        string memory metadataURI,
        uint256 parameterCount,
        string memory architecture
    ) external onlyModelOwner(name) {
        require(models[name].active, "Model is inactive");

        uint256 versionId = models[name].latestVersion + 1;

        versions[name][versionId] = ModelVersion({
            versionId: versionId,
            modelName: name,
            artifactHash: artifactHash,
            metadataURI: metadataURI,
            parameterCount: parameterCount,
            architecture: architecture,
            registrant: msg.sender,
            registeredAt: block.timestamp,
            verified: false,
            verificationCount: 0
        });

        models[name].latestVersion = versionId;
        totalVersions++;

        emit VersionPublished(name, versionId, artifactHash);
    }

    function verifyVersion(
        string memory name,
        uint256 versionId
    ) external onlyVerifier {
        require(versionId > 0 && versionId <= models[name].latestVersion, "Invalid version");
        require(!hasVerified[name][versionId][msg.sender], "Already verified");

        hasVerified[name][versionId][msg.sender] = true;
        versions[name][versionId].verificationCount++;

        if (versions[name][versionId].verificationCount >= verificationThreshold) {
            versions[name][versionId].verified = true;
        }

        emit ModelVerified(name, versionId, msg.sender);
    }

    function addVerifier(address verifier) external onlyAdmin {
        verifiers[verifier] = true;
        emit VerifierAdded(verifier);
    }

    function removeVerifier(address verifier) external onlyAdmin {
        verifiers[verifier] = false;
        emit VerifierRemoved(verifier);
    }

    function getModel(string memory name) external view returns (ModelEntry memory) {
        return models[name];
    }

    function getVersion(string memory name, uint256 versionId) external view returns (ModelVersion memory) {
        return versions[name][versionId];
    }

    function getLatestVerifiedVersion(string memory name) external view returns (ModelVersion memory) {
        uint256 latest = models[name].latestVersion;
        for (uint256 v = latest; v >= 1; v--) {
            if (versions[name][v].verified) {
                return versions[name][v];
            }
        }
        revert("No verified version found");
    }

    function verifyArtifactHash(
        string memory name,
        uint256 versionId,
        string memory expectedHash
    ) external view returns (bool) {
        return keccak256(bytes(versions[name][versionId].artifactHash)) ==
               keccak256(bytes(expectedHash));
    }

    function getModelCount() external view returns (uint256) {
        return totalModels;
    }

    function setVerificationThreshold(uint256 threshold) external onlyAdmin {
        verificationThreshold = threshold;
    }
}
