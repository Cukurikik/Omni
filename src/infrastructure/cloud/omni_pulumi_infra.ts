import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// Omni Infrastructure as Code (TypeScript / Pulumi)
// Infrastructure Layer
// Automates the deployment of Omni Unikernels onto AWS EC2 Nitro Enclaves
// for high-security, highly-scalable inference.

const config = new pulumi.Config();
const instanceType = config.get("instanceType") || "p4d.24xlarge"; // Default to A100 GPUs

// Create a VPC and Security Group for the Omni Cluster
const vpc = new aws.ec2.Vpc("omni-inference-vpc", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
});

const sg = new aws.ec2.SecurityGroup("omni-sg", {
    vpcId: vpc.id,
    ingress: [
        // Allow gRPC inference traffic
        { protocol: "tcp", fromPort: 50051, toPort: 50051, cidrBlocks: ["0.0.0.0/0"] },
        // Allow SSH for administration (Restricted in production)
        { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] },
    ],
    egress: [
        { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] },
    ],
});

// Deploy an Omni Unikernel instance
const ami = aws.ec2.getAmiOutput({
    filters: [
        { name: "name", values: ["omni-unikernel-x86_64-*"] },
    ],
    owners: ["self"],
    mostRecent: true,
});

const omniNode = new aws.ec2.Instance("omni-gpu-node-1", {
    instanceType: instanceType,
    vpcSecurityGroupIds: [sg.id],
    ami: ami.id,
    // Provisioning Nitro Enclaves for confidential computing
    enclaveOptions: {
        enabled: true,
    },
    tags: {
        Name: "Omni-GPU-Inference-Node",
        Environment: "Production",
        OmniVersion: "3.0.0"
    },
});

export const omniNodePublicIp = omniNode.publicIp;
export const omniNodePrivateIp = omniNode.privateIp;
