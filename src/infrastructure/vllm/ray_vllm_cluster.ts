import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// OMNI vLLM: Ray-based Distributed Serving Cluster
// Provisions EC2 instances with GPUs to run vLLM's tensor-parallel inference engine.
// Source: vllm-project/vllm

const config = new pulumi.Config();
const clusterName = "omni-vllm-serve";

// Security Group for vLLM API and Ray communication
const vllmSg = new aws.ec2.SecurityGroup(`${clusterName}-sg`, {
    description: "vLLM Inference Cluster Security Group",
    ingress: [
        { protocol: "tcp", fromPort: 8000, toPort: 8000, cidrBlocks: ["0.0.0.0/0"] }, // OpenAI API compat port
        { protocol: "tcp", fromPort: 0, toPort: 65535, self: true }, // Ray internode
        { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] } // SSH
    ],
    egress: [
        { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] },
    ],
});

// Using a standard Deep Learning AMI
const ami = aws.ec2.getAmi({
    filters: [{ name: "name", values: ["Deep Learning AMI GPU PyTorch*"] }],
    owners: ["amazon"],
    mostRecent: true,
});

// vLLM Head Node (Handles HTTP API and acts as Ray Head)
const headNode = new aws.ec2.Instance(`${clusterName}-head`, {
    instanceType: "p4d.24xlarge", // 8x A100 GPUs for massive LLMs
    ami: ami.then(a => a.id),
    vpcSecurityGroupIds: [vllmSg.id],
    tags: { Name: `${clusterName}-head` },
    userData: `#!/bin/bash
    pip install vllm ray
    ray start --head
    python -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-2-70b-chat-hf --tensor-parallel-size 8
    `,
});

export const vllmEndpoint = pulumi.interpolate`http://${headNode.publicIp}:8000/v1`;
