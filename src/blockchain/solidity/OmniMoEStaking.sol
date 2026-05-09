// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// OMNI MOTHER: Node Staking Contract for Decentralized MoE

contract OmniMoEStaking {
    mapping(address => uint256) public stakes;

    function stake() public payable {
        require(msg.value >= 1 ether, "Minimum 1 ETH required to run an expert node");
        stakes[msg.sender] += msg.value;
    }

    function isNodeActive(address node) public view returns (bool) {
        return stakes[node] >= 1 ether;
    }
}
