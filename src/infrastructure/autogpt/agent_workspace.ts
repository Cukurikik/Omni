import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// OMNI AUTOGPT: Isolated Agent Workspace
// Provisions an ephemeral Fargate container where AutoGPT can execute code securely.
// Source: Significant-Gravitas/AutoGPT

const config = new pulumi.Config();
const workspaceName = "omni-autogpt-sandbox";

// 1. Create a VPC without Internet Gateway for pure isolation (Airgapped)
const vpc = new aws.ec2.Vpc(`${workspaceName}-vpc`, {
    cidrBlock: "10.100.0.0/16",
    enableDnsSupport: true,
    enableDnsHostnames: true,
    tags: { Name: "autogpt-airgap-vpc" },
});

// 2. ECS Cluster for running agent workloads
const cluster = new aws.ecs.Cluster(`${workspaceName}-cluster`, {});

// 3. Task Definition for the Agent Sandbox (Python/Node runtime)
const taskDefinition = new aws.ecs.TaskDefinition(`${workspaceName}-task`, {
    family: "autogpt-sandbox",
    cpu: "256",
    memory: "512",
    networkMode: "awsvpc",
    requiresCompatibilities: ["FARGATE"],
    executionRoleArn: aws.iam.Role.get("ecsExecutionRole", "ecsTaskExecutionRole").arn,
    containerDefinitions: JSON.stringify([
        {
            name: "sandbox-env",
            image: "python:3.10-slim",
            command: ["sleep", "3600"], // Keep alive for remote agent execution
            essential: true,
            // Mount a temporary volume for the agent's file system actions
            readonlyRootFilesystem: true, 
        }
    ]),
});

export const clusterArn = cluster.arn;
export const taskDefArn = taskDefinition.arn;
