// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title OmniItsMoeDomain
 * @dev OMNI MOTHER: Decentralized Domain Registration for '.moe' namespaces.
 *      Production-grade contract with ENS-like mechanics, commit-reveal schemes, 
 *      and strict reentrancy protection.
 */

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract OmniItsMoeDomain is ReentrancyGuard, Ownable {
    
    struct DomainRecord {
        address owner;
        address resolver;
        uint64 expiresAt;
        string metadataURI;
    }

    mapping(bytes32 => DomainRecord) public domains;
    mapping(bytes32 => bytes32) public commitments;
    
    uint256 public constant MIN_COMMITMENT_AGE = 1 minutes;
    uint256 public constant MAX_COMMITMENT_AGE = 24 hours;
    uint256 public constant REGISTRATION_FEE = 0.01 ether;
    uint64 public constant REGISTRATION_DURATION = 365 days;

    event DomainRegistered(bytes32 indexed node, address indexed owner, uint64 expiresAt);
    event CommitmentMade(bytes32 indexed commitment);

    /**
     * @dev Step 1: Commit to a domain hash to prevent front-running.
     * @param commitment The hash of (domain_name + secret_salt)
     */
    function commit(bytes32 commitment) external {
        commitments[commitment] = bytes32(block.timestamp);
        emit CommitmentMade(commitment);
    }

    /**
     * @dev Step 2: Reveal the domain and register it.
     * @param name The plaintext domain name (e.g., "omni")
     * @param secret The secret salt used in the commitment
     */
    function register(string calldata name, bytes32 secret) external payable nonReentrant {
        require(msg.value >= REGISTRATION_FEE, "Insufficient fee");
        
        bytes32 node = keccak256(abi.encodePacked(name));
        bytes32 commitment = keccak256(abi.encodePacked(name, secret));
        
        uint256 commitTime = uint256(commitments[commitment]);
        require(commitTime > 0, "No commitment found");
        require(block.timestamp >= commitTime + MIN_COMMITMENT_AGE, "Commitment too fresh");
        require(block.timestamp <= commitTime + MAX_COMMITMENT_AGE, "Commitment expired");

        require(domains[node].expiresAt < block.timestamp, "Domain already registered");

        delete commitments[commitment]; // Prevent reuse

        domains[node] = DomainRecord({
            owner: msg.sender,
            resolver: msg.sender,
            expiresAt: uint64(block.timestamp + REGISTRATION_DURATION),
            metadataURI: ""
        });

        emit DomainRegistered(node, msg.sender, domains[node].expiresAt);
        
        // Refund excess
        if (msg.value > REGISTRATION_FEE) {
            payable(msg.sender).transfer(msg.value - REGISTRATION_FEE);
        }
    }
    
    function setMetadata(bytes32 node, string calldata uri) external {
        require(domains[node].owner == msg.sender, "Not the owner");
        domains[node].metadataURI = uri;
    }

    function withdraw() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
}
