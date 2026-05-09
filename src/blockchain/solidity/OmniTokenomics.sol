// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title OmniTokenomics
 * @dev OMNI MOTHER: Reward distribution token for compute sharing.
 */
contract OmniTokenomics is ERC20, Ownable {
    uint256 public constant HALVING_INTERVAL = 365 days;
    uint256 public nextHalving;
    uint256 public currentRewardRate;

    constructor() ERC20("OmniCompute", "OMNI") {
        _mint(msg.sender, 1000000 * 10 ** decimals()); // Premine
        nextHalving = block.timestamp + HALVING_INTERVAL;
        currentRewardRate = 50 * 10 ** decimals();
    }

    function rewardComputeProvider(address provider, uint256 cycles) external onlyOwner {
        checkHalving();
        uint256 reward = cycles * currentRewardRate;
        _mint(provider, reward);
    }

    function checkHalving() internal {
        if (block.timestamp >= nextHalving) {
            currentRewardRate /= 2;
            nextHalving = block.timestamp + HALVING_INTERVAL;
        }
    }
}
