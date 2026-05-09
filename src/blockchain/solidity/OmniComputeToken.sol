// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// OMNI Blockchain — Compute Token (ERC20)
// Rewards nodes for providing GPU compute to the OMNI cluster

contract OmniComputeToken {
    string public name = "Omni Compute Token";
    string public symbol = "OMNI";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) public balanceOf;
    address public owner;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Mint(address indexed to, uint256 value);

    constructor(uint256 initialSupply) {
        owner = msg.sender;
        totalSupply = initialSupply * (10 ** uint256(decimals));
        balanceOf[msg.sender] = totalSupply;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the network owner can execute this");
        _;
    }

    // Mint tokens to reward GPU miners who process LLM inferences
    function rewardComputeNode(address node, uint256 amount) public onlyOwner {
        totalSupply += amount;
        balanceOf[node] += amount;
        emit Mint(node, amount);
        emit Transfer(address(0), node, amount);
    }

    function transfer(address to, uint256 value) public returns (bool success) {
        require(balanceOf[msg.sender] >= value, "Insufficient balance");
        balanceOf[msg.sender] -= value;
        balanceOf[to] += value;
        emit Transfer(msg.sender, to, value);
        return true;
    }
}
