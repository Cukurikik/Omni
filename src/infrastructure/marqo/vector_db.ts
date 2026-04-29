import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// OMNI Infrastructure Layer: Pulumi Deployment for Marqo
// Provisions EC2 cluster and Load Balancer for Vector DB Nodes.

const config = new pulumi.Config();
const instanceType = config.get("instanceType") || "g4dn.xlarge"; // GPU accelerated
const amiId = aws.ec2.getAmi({
    filters: [{ name: "name", values: ["amzn2-ami-hvm-*-x86_64-ebs"] }],
    owners: ["amazon"],
    mostRecent: true,
}).then(ami => ami.id);

const vpc = new aws.ec2.Vpc("marqo-vpc", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
});

const subnet = new aws.ec2.Subnet("marqo-subnet", {
    vpcId: vpc.id,
    cidrBlock: "10.0.1.0/24",
    mapPublicIpOnLaunch: true,
});

const sg = new aws.ec2.SecurityGroup("marqo-sg", {
    vpcId: vpc.id,
    ingress: [
        { protocol: "tcp", fromPort: 8882, toPort: 8882, cidrBlocks: ["0.0.0.0/0"] }, // Marqo API
        { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] },    // SSH
    ],
    egress: [
        { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] },
    ],
});

// Launch 3 Marqo Nodes
const nodes = [];
for (let i = 1; i <= 3; i++) {
    const node = new aws.ec2.Instance(`marqo-node-${i}`, {
        instanceType: instanceType,
        vpcSecurityGroupIds: [sg.id],
        subnetId: subnet.id,
        ami: amiId,
        userData: `#!/bin/bash
        docker run -d -p 8882:8882 marqoai/marqo:latest
        `,
        tags: { Name: `Marqo-VectorNode-${i}` },
    });
    nodes.push(node);
}

export const marqoEndpoint = nodes[0].publicIp.apply(ip => `http://${ip}:8882`);
