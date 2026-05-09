// @omni-layer Infrastructure | @omni-lang Pulumi (TypeScript) | @omni-batch 17
// @omni-description GPU cluster IaC: Pulumi program for provisioning
// multi-GPU inference cluster with auto-scaling and model cache on AWS.

import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const config = new pulumi.Config();
const clusterName = config.get("clusterName") || "omni-inference";
const gpuInstanceType = config.get("gpuInstance") || "g5.xlarge";
const minInstances = config.getNumber("minInstances") || 1;
const maxInstances = config.getNumber("maxInstances") || 10;

// S3 Bucket for model storage
const modelBucket = new aws.s3.Bucket(`${clusterName}-models`, {
    versioning: { enabled: true },
    tags: { Project: "OMNI", Layer: "Infrastructure", Batch: "17" },
});

// ECR Repository for inference container
const ecrRepo = new aws.ecr.Repository(`${clusterName}-inference`, {
    imageTagMutability: "MUTABLE",
    imageScanningConfiguration: { scanOnPush: true },
});

// VPC
const vpc = new aws.ec2.Vpc(`${clusterName}-vpc`, {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
    tags: { Name: `${clusterName}-vpc`, Project: "OMNI" },
});

const subnet = new aws.ec2.Subnet(`${clusterName}-subnet`, {
    vpcId: vpc.id,
    cidrBlock: "10.0.1.0/24",
    mapPublicIpOnLaunch: true,
    tags: { Name: `${clusterName}-subnet` },
});

// Security Group
const sgInference = new aws.ec2.SecurityGroup(`${clusterName}-sg`, {
    vpcId: vpc.id,
    ingress: [
        { protocol: "tcp", fromPort: 8080, toPort: 8080, cidrBlocks: ["0.0.0.0/0"] },
        { protocol: "tcp", fromPort: 50051, toPort: 50051, cidrBlocks: ["0.0.0.0/0"] },
    ],
    egress: [{ protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] }],
});

// ECS Cluster
const cluster = new aws.ecs.Cluster(`${clusterName}-cluster`, {
    settings: [{ name: "containerInsights", value: "enabled" }],
    tags: { Project: "OMNI", Component: "InferenceCluster" },
});

// CloudWatch Log Group
const logGroup = new aws.cloudwatch.LogGroup(`${clusterName}-logs`, {
    retentionInDays: 30,
});

// Auto Scaling
const scalingTarget = new aws.appautoscaling.Target(`${clusterName}-scaling`, {
    maxCapacity: maxInstances,
    minCapacity: minInstances,
    resourceId: pulumi.interpolate`service/${cluster.name}/${clusterName}-svc`,
    scalableDimension: "ecs:service:DesiredCount",
    serviceNamespace: "ecs",
});

const scalingPolicy = new aws.appautoscaling.Policy(`${clusterName}-cpu-scaling`, {
    policyType: "TargetTrackingScaling",
    resourceId: scalingTarget.resourceId,
    scalableDimension: scalingTarget.scalableDimension,
    serviceNamespace: scalingTarget.serviceNamespace,
    targetTrackingScalingPolicyConfiguration: {
        predefinedMetricSpecification: {
            predefinedMetricType: "ECSServiceAverageCPUUtilization",
        },
        targetValue: 65,
        scaleInCooldown: 120,
        scaleOutCooldown: 60,
    },
});

// Exports
export const clusterArn = cluster.arn;
export const modelBucketName = modelBucket.bucket;
export const ecrRepoUrl = ecrRepo.repositoryUrl;
export const vpcId = vpc.id;
