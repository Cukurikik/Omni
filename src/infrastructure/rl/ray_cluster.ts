import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// OMNI RL - Ray Cluster Infrastructure as Code (Pulumi)
// Provisioning auto-scaling GPU cluster for distributed RL workloads

export class RayCluster {
    public readonly clusterName: string;
    public readonly headNodeIp: pulumi.Output<string>;

    constructor(name: string, instanceType: string = "p4d.24xlarge") {
        this.clusterName = name;

        // Security group for Ray nodes
        const raySecurityGroup = new aws.ec2.SecurityGroup(`${name}-ray-sg`, {
            description: "Allow intra-cluster communication for Ray",
            ingress: [
                { protocol: "tcp", fromPort: 0, toPort: 65535, self: true }, // Ray internode
                { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] }, // SSH
                { protocol: "tcp", fromPort: 8265, toPort: 8265, cidrBlocks: ["0.0.0.0/0"] }, // Ray Dashboard
            ],
            egress: [
                { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] },
            ],
        });

        // IAM Role for nodes
        const rayRole = new aws.iam.Role(`${name}-ray-role`, {
            assumeRolePolicy: aws.iam.assumeRolePolicyForPrincipal({ Service: "ec2.amazonaws.com" }),
        });

        // AMI - Deep Learning Base AMI
        const ami = aws.ec2.getAmiOutput({
            filters: [
                { name: "name", values: ["Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04) *"] },
            ],
            owners: ["amazon"],
            mostRecent: true,
        });

        // Head Node
        const headNode = new aws.ec2.Instance(`${name}-head-node`, {
            instanceType: "m5.2xlarge", // CPU node for head
            vpcSecurityGroupIds: [raySecurityGroup.id],
            ami: ami.id,
            tags: { Name: `${name}-head` },
            userData: `#!/bin/bash
                pip install ray[default]
                ray start --head --port=6379 --dashboard-host=0.0.0.0
            `,
        });

        // Worker Auto Scaling Group
        const launchTemplate = new aws.ec2.LaunchTemplate(`${name}-worker-lt`, {
            instanceType: instanceType, // GPU nodes
            imageId: ami.id,
            vpcSecurityGroupIds: [raySecurityGroup.id],
            userData: headNode.privateIp.apply(ip => Buffer.from(`#!/bin/bash
                pip install ray[default]
                ray start --address='${ip}:6379'
            `).toString('base64')),
        });

        const asg = new aws.autoscaling.Group(`${name}-worker-asg`, {
            vpcZoneIdentifiers: aws.ec2.getSubnetsOutput({ filters: [{ name: "default-for-az", values: ["true"] }] }).ids,
            desiredCapacity: 2,
            minSize: 1,
            maxSize: 10,
            launchTemplate: {
                id: launchTemplate.id,
                version: "$Latest",
            },
            tags: [{ key: "Name", value: `${name}-worker`, propagateAtLaunch: true }],
        });

        this.headNodeIp = headNode.publicIp;
    }
}
