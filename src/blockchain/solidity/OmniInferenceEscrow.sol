// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// OMNI Blockchain — Inference Escrow
// Smart contract handling trustless payment for decentralized compute tasks

contract OmniInferenceEscrow {
    
    struct Task {
        address client;
        address node;
        uint256 bounty;
        bool completed;
    }

    mapping(bytes32 => Task) public tasks;
    address public arbiter; // OMNI Network oracle

    constructor() {
        arbiter = msg.sender;
    }

    function createTask(bytes32 taskId) public payable {
        require(msg.value > 0, "Bounty must be greater than 0");
        require(tasks[taskId].client == address(0), "Task already exists");

        tasks[taskId] = Task({
            client: msg.sender,
            node: address(0),
            bounty: msg.value,
            completed: false
        });
    }

    function completeTask(bytes32 taskId, address nodeNode) public {
        require(msg.sender == arbiter, "Only arbiter can verify completion");
        require(!tasks[taskId].completed, "Task already completed");
        require(tasks[taskId].client != address(0), "Task does not exist");

        tasks[taskId].node = nodeNode;
        tasks[taskId].completed = true;

        // Release funds to the compute node
        payable(nodeNode).transfer(tasks[taskId].bounty);
    }
}
