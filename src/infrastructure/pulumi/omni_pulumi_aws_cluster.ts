import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// OMNI Infrastructure Layer
// Pulumi script for provisioning a massive AWS GPU Cluster (P4d instances) for distributed training

const config = new pulumi.Config();
const instanceCount = config.getNumber("gpuNodeCount") || 8;

const vpc = new aws.ec2.Vpc("omni-training-vpc", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
    enableDnsSupport: true,
});

const subnet = new aws.ec2.Subnet("omni-training-subnet", {
    vpcId: vpc.id,
    cidrBlock: "10.0.1.0/24",
    availabilityZone: "us-west-2a",
    mapPublicIpOnLaunch: true,
});

const ami = aws.ec2.getAmiOutput({
    mostRecent: true,
    owners: ["amazon"],
    filters: [{
        name: "name",
        values: ["Deep Learning AMI GPU PyTorch * (Ubuntu 20.04) *"],
    }],
});

const securityGroup = new aws.ec2.SecurityGroup("omni-cluster-sg", {
    vpcId: vpc.id,
    ingress: [
        { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] },
        { protocol: "tcp", fromPort: 29500, toPort: 29500, cidrBlocks: ["10.0.0.0/16"] }, // PyTorch distributed
    ],
    egress: [
        { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] },
    ],
});

export const instanceIps: pulumi.Output<string>[] = [];

for (let i = 0; i < instanceCount; i++) {
    const gpuNode = new aws.ec2.Instance(`omni-p4d-node-${i}`, {
        instanceType: "p4d.24xlarge", // 8x A100 GPUs per node
        ami: ami.id,
        subnetId: subnet.id,
        vpcSecurityGroupIds: [securityGroup.id],
        keyName: "omni-cluster-key",
        tags: {
            Name: `omni-gpu-node-${i}`,
            Cluster: "OMNI_MASTER_TRAINING"
        }
    });

    instanceIps.push(gpuNode.publicIp);
}
