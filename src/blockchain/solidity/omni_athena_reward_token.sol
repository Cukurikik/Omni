// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// OMNI Framework - AthenaOS Reward Token
// ERC-20 token used to incentivize compute nodes participating in AthenaOS swarms

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract OmniAthenaToken is ERC20, Ownable {
    mapping(address => bool) public authorizedNodes;

    event NodeAuthorized(address indexed node);
    event TaskRewarded(address indexed node, uint256 amount, string taskId);

    constructor() ERC20("OMNI Athena", "OATH") {}

    function authorizeNode(address node) external onlyOwner {
        authorizedNodes[node] = true;
        emit NodeAuthorized(node);
    }

    function rewardTaskCompletion(address node, uint256 amount, string memory taskId) external onlyOwner {
        require(authorizedNodes[node], "OMNI: Node is not authorized to receive rewards");
        _mint(node, amount);
        emit TaskRewarded(node, amount, taskId);
    }
}
