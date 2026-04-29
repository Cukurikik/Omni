// OMNI HIGGSFIELD: GPU Cluster Deployment
// Pulumi Infrastructure-as-Code script to provision a fault-tolerant GPU cluster for trillion-parameter training.
// Source: higgsfield-ai/higgsfield

import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// VPC specifically optimized for EFA (Elastic Fabric Adapter) interconnects
const vpc = new aws.ec2.Vpc("higgsfield-vpc", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
});

const subnet = new aws.ec2.Subnet("higgsfield-subnet", {
    vpcId: vpc.id,
    cidrBlock: "10.0.1.0/24",
    availabilityZone: "us-east-1a",
});

const clusterSg = new aws.ec2.SecurityGroup("higgsfield-cluster-sg", {
    vpcId: vpc.id,
    description: "Allow NCCL and RDMA traffic",
    ingress: [
        { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] },
        { protocol: "tcp", fromPort: 0, toPort: 65535, self: true }, // Allow all intra-cluster traffic for NCCL
    ],
    egress: [{ protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] }],
});

// Define the GPU Node Group (e.g., p4d.24xlarge for A100s)
const gpuNodeGroup = new aws.autoscaling.Group("higgsfield-gpu-asg", {
    vpcZoneIdentifiers: [subnet.id],
    desiredCapacity: 4, // 4 nodes = 32 GPUs total
    minSize: 4,
    maxSize: 8,
    launchTemplate: {
        id: new aws.ec2.LaunchTemplate("higgsfield-gpu-lt", {
            instanceType: "p4d.24xlarge",
            imageId: "ami-0c55b159cbfafe1f0", // Deep Learning AMI GPU
            vpcSecurityGroupIds: [clusterSg.id],
            userData: Buffer.from(`#!/bin/bash
                echo "Starting Higgsfield Orchestration Agent"
                systemctl start higgsfield-agent
            `).toString('base64'),
        }).id,
    },
});

export const clusterName = gpuNodeGroup.name;
