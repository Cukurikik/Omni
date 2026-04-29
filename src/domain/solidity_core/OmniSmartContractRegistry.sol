// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title OmniSmartContractRegistry
 * @dev OMNI Blockchain Layer
 * 
 * Decentralized hash registry for tracking AI Model provenance,
 * training datasets (Olmo), and zero-mock verification footprints.
 */
contract OmniSmartContractRegistry {
    
    struct EngineManifest {
        string engineName;
        string version;
        bytes32 codeHash;
        uint256 registeredAt;
        bool isZeroMockCompliant;
    }

    mapping(bytes32 => EngineManifest) public registry;
    address public owner;

    event EngineRegistered(bytes32 indexed engineId, string name, bool compliant);

    error Unauthorized();
    error EngineAlreadyRegistered();

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        if (msg.sender != owner) revert Unauthorized();
        _;
    }

    /**
     * @dev Register a new OMNI engine footprint
     */
    function registerEngine(
        bytes32 engineId,
        string memory name,
        string memory version,
        bytes32 codeHash,
        bool isZeroMock
    ) external onlyOwner {
        if (registry[engineId].registeredAt != 0) {
            revert EngineAlreadyRegistered();
        }

        registry[engineId] = EngineManifest({
            engineName: name,
            version: version,
            codeHash: codeHash,
            registeredAt: block.timestamp,
            isZeroMockCompliant: isZeroMock
        });

        emit EngineRegistered(engineId, name, isZeroMock);
    }

    /**
     * @dev Check if a specific engine hash exists and is compliant
     */
    function verifyCompliance(bytes32 engineId) external view returns (bool) {
        return registry[engineId].isZeroMockCompliant;
    }
}
