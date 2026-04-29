// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// OMNI Blockchain & Smart Contract Layer
// Handles distributed compute resource allocation via tokenized economy

contract OmniComputeToken {
    string public name = "Omni Compute Token";
    string public symbol = "OCT";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) public balanceOf;

    error InsufficientBalance(uint256 requested, uint256 available);

    constructor(uint256 _initialSupply) {
        totalSupply = _initialSupply * 10 ** uint256(decimals);
        balanceOf[msg.sender] = totalSupply;
    }

    // Monadic-inspired error handling via custom errors
    function transfer(address _to, uint256 _value) public returns (bool success) {
        if (balanceOf[msg.sender] < _value) {
            revert InsufficientBalance(_value, balanceOf[msg.sender]);
        }
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        return true;
    }
}
