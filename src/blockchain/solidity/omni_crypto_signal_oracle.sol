// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title OmniCryptoSignalOracle
 * @dev OMNI Framework - Smart contract to log FinBERT crypto sentiment signals
 * immutably on-chain for algorithmic trading bots to consume via Web3.
 */
contract OmniCryptoSignalOracle {
    
    address public owner;
    
    struct Signal {
        string symbol;
        string action; // "BUY", "SELL", "HOLD"
        uint256 confidenceBasisPoints; // e.g. 8500 = 85.00%
        uint256 timestamp;
    }
    
    // Mapping of Symbol -> Latest Signal
    mapping(string => Signal) public latestSignals;
    
    event SignalUpdated(string indexed symbol, string action, uint256 confidence);

    modifier onlyOwner() {
        require(msg.sender == owner, "OMNI: Caller is not the oracle owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function updateSignal(
        string memory _symbol, 
        string memory _action, 
        uint256 _confidence
    ) external onlyOwner {
        
        Signal memory newSignal = Signal({
            symbol: _symbol,
            action: _action,
            confidenceBasisPoints: _confidence,
            timestamp: block.timestamp
        });
        
        latestSignals[_symbol] = newSignal;
        
        emit SignalUpdated(_symbol, _action, _confidence);
    }
    
    function getSignal(string memory _symbol) external view returns (Signal memory) {
        return latestSignals[_symbol];
    }
}
