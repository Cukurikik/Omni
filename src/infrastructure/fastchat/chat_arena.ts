import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// OMNI FASTCHAT: Distributed Chat Arena
// Provisions an Auto Scaling Group of worker nodes and a Redis instance for routing.
// Source: lm-sys/FastChat

const config = new pulumi.Config();
const arenaName = "omni-fastchat-arena";

// 1. VPC and Subnets (Simplified)
const vpc = new aws.ec2.Vpc(`${arenaName}-vpc`, { cidrBlock: "10.0.0.0/16" });
const subnet = new aws.ec2.Subnet(`${arenaName}-subnet`, { vpcId: vpc.id, cidrBlock: "10.0.1.0/24" });

// 2. Redis Cluster for FastChat state management and worker discovery
const redisSubnetGroup = new aws.elasticache.SubnetGroup(`${arenaName}-redis-subnet`, {
    subnetIds: [subnet.id],
});

const redis = new aws.elasticache.Cluster(`${arenaName}-redis`, {
    engine: "redis",
    nodeType: "cache.t3.micro",
    numCacheNodes: 1,
    subnetGroupName: redisSubnetGroup.name,
    port: 6379,
});

// 3. Worker Node Launch Template (GPU Instances)
const workerAmi = aws.ec2.getAmi({
    filters: [{ name: "name", values: ["Deep Learning AMI GPU PyTorch*"] }],
    owners: ["amazon"],
    mostRecent: true,
});

const workerTemplate = new aws.ec2.LaunchTemplate(`${arenaName}-worker-lt`, {
    imageId: workerAmi.then(a => a.id),
    instanceType: "g5.2xlarge", // Single A10G for smaller models
    userData: pulumi.all([redis.cacheNodes[0].address]).apply(([redisAddr]) => 
        Buffer.from(`#!/bin/bash
        pip install fschat
        python3 -m fastchat.serve.model_worker --model-path meta-llama/Llama-2-7b-chat-hf --controller-address http://${redisAddr}:21001
        `).toString('base64')
    ),
});

// 4. Auto Scaling Group for Workers
const workerAsg = new aws.autoscaling.Group(`${arenaName}-asg`, {
    vpcZoneIdentifiers: [subnet.id],
    desiredCapacity: 2,
    minSize: 1,
    maxSize: 10,
    launchTemplate: {
        id: workerTemplate.id,
        version: "$Latest",
    },
});

export const redisEndpoint = redis.cacheNodes[0].address;
