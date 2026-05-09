// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// OMNI MOTHER: Decentralized MoE Expert Payment Contract
// Blockchain Layer

contract OmniMoEPayment {
    mapping(address => uint256) public expertBalances;

    function rewardExpert(address expert, uint256 tokensProcessed) public {
        // Reward 1 wei per token processed
        expertBalances[expert] += tokensProcessed;
    }

    function withdraw() public {
        uint256 amount = expertBalances[msg.sender];
        require(amount > 0, "No funds");
        expertBalances[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
    }
}
