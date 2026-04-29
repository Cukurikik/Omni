import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// OMNI MILVUS: Distributed Vector Database Cluster
// Provisions EC2 instances and EBS volumes for Milvus Query and Data nodes.
// Source: milvus-io/milvus

const config = new pulumi.Config();
const clusterName = "omni-milvus-vector";

// Security Group
const milvusSg = new aws.ec2.SecurityGroup(`${clusterName}-sg`, {
    description: "Milvus Vector DB Security Group",
    ingress: [
        { protocol: "tcp", fromPort: 19530, toPort: 19530, cidrBlocks: ["10.0.0.0/8"] }, // Milvus GRPC inside VPC
        { protocol: "tcp", fromPort: 2379, toPort: 2379, self: true }, // etcd internode
        { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] } // SSH
    ],
    egress: [
        { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] },
    ],
});

// Ubuntu AMI
const ami = aws.ec2.getAmi({
    filters: [{ name: "name", values: ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"] }],
    owners: ["099720109477"], // Canonical
    mostRecent: true,
});

// Milvus Root Coord / Query Node
const queryNode = new aws.ec2.Instance(`${clusterName}-query`, {
    instanceType: "c6i.4xlarge", // High CPU for similarity math
    ami: ami.then(a => a.id),
    vpcSecurityGroupIds: [milvusSg.id],
    tags: { Name: `${clusterName}-query-node` },
    userData: `#!/bin/bash
    # Mocking docker-compose setup for Milvus
    curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh
    bash standalone_embed.sh start
    `,
});

// Data Nodes with high IOPS storage
const dataNode = new aws.ec2.Instance(`${clusterName}-data`, {
    instanceType: "r6i.2xlarge", // Memory optimized for indexing
    ami: ami.then(a => a.id),
    vpcSecurityGroupIds: [milvusSg.id],
    rootBlockDevice: {
        volumeType: "io2",
        iops: 5000,
        volumeSize: 500,
    },
    tags: { Name: `${clusterName}-data-node` },
});

export const milvusGrpcEndpoint = pulumi.interpolate`${queryNode.privateIp}:19530`;
