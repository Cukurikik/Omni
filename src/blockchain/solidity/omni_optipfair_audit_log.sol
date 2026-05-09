// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// OMNI Framework - On-Chain Audit Log for Optipfair
// Ensures immutable, tamper-proof records of AI bias audits

contract OmniOptipfairAuditLog {
    
    struct AuditRecord {
        uint256 timestamp;
        string modelVersion;
        string auditorHash;
        uint256 overallFairnessScore; // multiplied by 10000 for precision
        bool passed;
    }

    AuditRecord[] public auditHistory;
    address public admin;

    event AuditLogged(uint256 indexed index, string modelVersion, bool passed);

    constructor() {
        admin = msg.sender;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "OMNI: Only admin can log audits");
        _;
    }

    function logAudit(
        string memory _modelVersion,
        string memory _auditorHash,
        uint256 _score,
        bool _passed
    ) external onlyAdmin {
        auditHistory.push(AuditRecord({
            timestamp: block.timestamp,
            modelVersion: _modelVersion,
            auditorHash: _auditorHash,
            overallFairnessScore: _score,
            passed: _passed
        }));

        emit AuditLogged(auditHistory.length - 1, _modelVersion, _passed);
    }

    function getAuditCount() external view returns (uint256) {
        return auditHistory.length;
    }
}
