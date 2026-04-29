import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// OMNI LLM-RL: Ray Cluster Provisioning
// Sets up a distributed computing cluster using Ray, necessary for parallel RLHF environment rollouts.
// Source: ray-project/ray (contextual for RL)

const config = new pulumi.Config();
const clusterName = "omni-ray-rlhf";

// Security Group for Ray Communication
const raySg = new aws.ec2.SecurityGroup(`${clusterName}-sg`, {
    description: "Allow Ray intra-cluster communication",
    ingress: [
        { protocol: "tcp", fromPort: 0, toPort: 65535, self: true }, // Internal full access
        { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] }, // SSH
        { protocol: "tcp", fromPort: 8265, toPort: 8265, cidrBlocks: ["0.0.0.0/0"] } // Ray Dashboard
    ],
    egress: [
        { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] },
    ],
});

const ami = aws.ec2.getAmi({
    filters: [{ name: "name", values: ["Deep Learning AMI (Ubuntu 20.04) Version*"] }],
    owners: ["amazon"],
    mostRecent: true,
});

// Ray Head Node
const headNode = new aws.ec2.Instance(`${clusterName}-head`, {
    instanceType: "g4dn.xlarge", // GPU instance for the policy model
    ami: ami.then(a => a.id),
    vpcSecurityGroupIds: [raySg.id],
    tags: { Name: `${clusterName}-head` },
    userData: `#!/bin/bash
    pip install ray[default]
    ray start --head --port=6379 --dashboard-host=0.0.0.0
    `,
});

// Ray Worker Nodes (CPU intensive for environment simulation)
const workerNodes = [];
for (let i = 0; i < 3; i++) {
    workerNodes.push(new aws.ec2.Instance(`${clusterName}-worker-${i}`, {
        instanceType: "c5.2xlarge", // Compute optimized
        ami: ami.then(a => a.id),
        vpcSecurityGroupIds: [raySg.id],
        tags: { Name: `${clusterName}-worker-${i}` },
        userData: pulumi.interpolate`#!/bin/bash
        pip install ray[default]
        ray start --address=${headNode.privateIp}:6379
        `,
    }));
}

export const rayDashboardUrl = pulumi.interpolate`http://${headNode.publicIp}:8265`;
export const headPrivateIp = headNode.privateIp;
