// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title OmniMoEComputeMarket
 * @dev OMNI Framework - Decentralized marketplace for renting GPU compute
 * specifically tailored for hosting and serving MoE Expert shards.
 */
contract OmniMoEComputeMarket {
    
    struct Provider {
        address wallet;
        uint256 availableGpus;
        uint256 pricePerToken; // In wei
        bool isVerified;
        string endpoint; // URL/IP of the SGLang/vLLM worker
    }

    mapping(address => Provider) public providers;
    address[] public activeProviders;

    event ProviderRegistered(address indexed wallet, uint256 gpus, uint256 price);
    event ComputeRented(address indexed tenant, address indexed provider, uint256 allocatedTokens);

    /**
     * @dev Register a node to host MoE Experts.
     */
    function registerProvider(uint256 _availableGpus, uint256 _pricePerToken, string memory _endpoint) external {
        require(_availableGpus > 0, "Must offer at least 1 GPU");
        
        if (providers[msg.sender].availableGpus == 0) {
            activeProviders.push(msg.sender);
        }
        
        providers[msg.sender] = Provider({
            wallet: msg.sender,
            availableGpus: _availableGpus,
            pricePerToken: _pricePerToken,
            isVerified: false,
            endpoint: _endpoint
        });

        emit ProviderRegistered(msg.sender, _availableGpus, _pricePerToken);
    }

    /**
     * @dev Tenant pays ETH to rent compute from a specific provider for inference.
     */
    function rentCompute(address _providerAddress, uint256 _estimatedTokens) external payable {
        Provider storage prov = providers[_providerAddress];
        require(prov.availableGpus > 0, "Provider not found or inactive");
        
        uint256 requiredPayment = _estimatedTokens * prov.pricePerToken;
        require(msg.value >= requiredPayment, "Insufficient funds provided for requested tokens");

        // Transfer funds to provider
        payable(_providerAddress).transfer(msg.value);

        emit ComputeRented(msg.sender, _providerAddress, _estimatedTokens);
    }

    // Function to retrieve all active endpoints for the Router to connect
    function getActiveEndpoints() external view returns (string[] memory) {
        string[] memory endpoints = new string[](activeProviders.length);
        for(uint i = 0; i < activeProviders.length; i++) {
            endpoints[i] = providers[activeProviders[i]].endpoint;
        }
        return endpoints;
    }
}
