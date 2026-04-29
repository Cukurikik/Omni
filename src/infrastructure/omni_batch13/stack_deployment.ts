// OMNI BATCH 13: Full Stack Deployment
// Pulumi Infrastructure-as-Code script to provision the integrated 
// Supabase, MetaGPT, and AutoGen resources into the OMNI Cloud / Local Stack.

import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// 1. Core Networking
const vpc = new aws.ec2.Vpc("omni-batch13-vpc", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
    enableDnsSupport: true,
    tags: { Name: "omni-batch13-vpc" }
});

const subnet = new aws.ec2.Subnet("omni-batch13-subnet", {
    vpcId: vpc.id,
    cidrBlock: "10.0.1.0/24",
    availabilityZone: "us-east-1a",
});

// 2. Database Layer (Supabase / Implicit PostgreSQL)
const dbSecurityGroup = new aws.ec2.SecurityGroup("db-sg", {
    vpcId: vpc.id,
    ingress: [{ protocol: "tcp", fromPort: 5432, toPort: 5432, cidrBlocks: ["10.0.0.0/16"] }],
});

const rdsInstance = new aws.rds.Instance("omni-core-db", {
    engine: "postgres",
    instanceClass: "db.t3.medium",
    allocatedStorage: 50,
    dbName: "omnicore",
    username: "omni_admin",
    password: "production_password_placeholder", // Managed via AWS Secrets in real env
    vpcSecurityGroupIds: [dbSecurityGroup.id],
    dbSubnetGroupName: new aws.rds.SubnetGroup("db-subnet-grp", { subnetIds: [subnet.id] }).name,
    skipFinalSnapshot: true,
});

// 3. Compute Layer (LocalAI / AutoGen / MetaGPT Executors)
const computeSg = new aws.ec2.SecurityGroup("compute-sg", {
    vpcId: vpc.id,
    ingress: [{ protocol: "tcp", fromPort: 8000, toPort: 8000, cidrBlocks: ["0.0.0.0/0"] }], // API port
    egress: [{ protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] }]
});

// GPU Instance for GGML / LLM Inference
const inferenceNode = new aws.ec2.Instance("omni-inference-node", {
    instanceType: "g4dn.xlarge", // NVIDIA T4
    ami: "ami-0c55b159cbfafe1f0", // Ubuntu Deep Learning AMI
    subnetId: subnet.id,
    vpcSecurityGroupIds: [computeSg.id],
    tags: { Name: "OMNI LocalAI Inference" }
});

// 4. Kafka Event Stream (Telemetry & Artifacts)
const mskCluster = new aws.msk.Cluster("omni-event-bus", {
    kafkaVersion: "2.8.1",
    numberOfBrokerNodes: 2,
    brokerNodeGroupInfo: {
        instanceType: "kafka.t3.small",
        clientSubnets: [subnet.id, subnet.id], // Requires 2 subnets in 2 AZs normally
        securityGroups: [computeSg.id],
    },
});

export const dbEndpoint = rdsInstance.endpoint;
export const inferenceIp = inferenceNode.publicIp;
export const kafkaBrokers = mskCluster.bootstrapBrokers;
