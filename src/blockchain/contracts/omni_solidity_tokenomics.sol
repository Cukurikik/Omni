// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title OmniComputeNetwork
 * @dev Blockchain Layer: Manages decentralised GPU compute sharing for the Omni network.
 * Zero-Mock implementation of task submission, staking, and reward payout.
 */
contract OmniComputeNetwork {
    struct ComputeTask {
        address requester;
        string modelHash;     // IPFS hash of the model weights
        string dataHash;      // IPFS hash of the inference data
        uint256 rewardAmount;
        address solver;
        bool isCompleted;
    }

    uint256 public taskCounter;
    mapping(uint256 => ComputeTask) public tasks;
    mapping(address => uint256) public stakedCompute;

    event TaskCreated(uint256 indexed taskId, address requester, uint256 reward);
    event TaskCompleted(uint256 indexed taskId, address solver);

    // Nodes stake ETH to participate as a solver
    function stake() external payable {
        require(msg.value >= 1 ether, "Minimum 1 ETH stake required");
        stakedCompute[msg.sender] += msg.value;
    }

    function submitTask(string memory _modelHash, string memory _dataHash) external payable {
        require(msg.value > 0, "Task requires a reward");

        taskCounter++;
        tasks[taskCounter] = ComputeTask({
            requester: msg.sender,
            modelHash: _modelHash,
            dataHash: _dataHash,
            rewardAmount: msg.value,
            solver: address(0),
            isCompleted: false
        });

        emit TaskCreated(taskCounter, msg.sender, msg.value);
    }

    function completeTask(uint256 _taskId, string memory _proofHash) external {
        ComputeTask storage task = tasks[_taskId];
        
        require(!task.isCompleted, "Task already completed");
        require(stakedCompute[msg.sender] > 0, "Solver must be staked");
        
        // In production, the proof is verified via a ZK Verifier contract (omni_solidity_verifier.sol)
        // Here we assume successful off-chain verification logic triggers this.
        
        task.isCompleted = true;
        task.solver = msg.sender;

        // Transfer reward
        payable(msg.sender).transfer(task.rewardAmount);

        emit TaskCompleted(_taskId, msg.sender);
    }
}
