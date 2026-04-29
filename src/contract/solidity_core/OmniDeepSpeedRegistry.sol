// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Omni DeepSpeed Registry (Solidity)
// Smart Contract Layer: Deterministic registry for distributed training block allocations.

contract OmniDeepSpeedRegistry {
    
    struct BlockAllocation {
        uint256 blockId;
        uint256 sizeBytes;
        bool isActive;
    }

    mapping(address => BlockAllocation[]) private nodeAllocations;

    event AllocationRegistered(address indexed node, uint256 blockId, uint256 sizeBytes);

    function registerAllocation(uint256 _blockId, uint256 _sizeBytes) external {
        require(_sizeBytes > 0, "OMNI_ERR: Allocation size must be strictly positive");
        
        nodeAllocations[msg.sender].push(BlockAllocation({
            blockId: _blockId,
            sizeBytes: _sizeBytes,
            isActive: true
        }));

        emit AllocationRegistered(msg.sender, _blockId, _sizeBytes);
    }
}
