// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title OmniTokenStorage
 * @dev OMNI Framework - Storage layer for OMNI Compute Tokens.
 * Decouples state from logic to allow proxy upgrades.
 */
contract OmniTokenStorage {
    
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;

    uint256 private _totalSupply;
    string private _name = "Omni Compute Token";
    string private _symbol = "OCT";

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    function name() public view returns (string memory) {
        return _name;
    }

    function symbol() public view returns (string memory) {
        return _symbol;
    }

    function totalSupply() public view returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) public view returns (uint256) {
        return _balances[account];
    }

    // Note: State modifying functions (transfer, mint, etc.) would be in a separate Logic contract
    // that delegates calls to this storage, or implemented here if not using proxy patterns.
}
