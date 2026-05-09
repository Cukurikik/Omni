// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title OmniGovernance
 * @dev OMNI MOTHER: DAO logic for Omni protocol upgrades.
 */
contract OmniGovernance {
    struct Proposal {
        uint256 id;
        address proposer;
        string description;
        uint256 votesFor;
        uint256 votesAgainst;
        bool executed;
    }

    mapping(uint256 => Proposal) public proposals;
    uint256 public proposalCount;

    event ProposalCreated(uint256 id, string desc);
    event Voted(uint256 id, bool support, address voter);

    function createProposal(string memory description) external {
        proposalCount++;
        proposals[proposalCount] = Proposal({
            id: proposalCount,
            proposer: msg.sender,
            description: description,
            votesFor: 0,
            votesAgainst: 0,
            executed: false
        });
        emit ProposalCreated(proposalCount, description);
    }

    function vote(uint256 id, bool support) external {
        require(id > 0 && id <= proposalCount, "Invalid proposal");
        Proposal storage p = proposals[id];
        require(!p.executed, "Already executed");

        if (support) p.votesFor++;
        else p.votesAgainst++;

        emit Voted(id, support, msg.sender);
    }
}
