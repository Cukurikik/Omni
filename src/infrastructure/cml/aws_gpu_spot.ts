import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// OMNI CML: Continuous Machine Learning IaC
// Pulumi script to automatically provision ephemeral EC2 Spot instances for model training.
// Source: iterative/cml

const config = new pulumi.Config();
const instanceType = config.get("instanceType") || "g4dn.xlarge"; // NVIDIA T4 GPU

// Create a Security Group allowing SSH and internal training ports
const sg = new aws.ec2.SecurityGroup("cml-runner-sg", {
    description: "Allow SSH and CML worker traffic",
    ingress: [
        { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] },
        { protocol: "tcp", fromPort: 8080, toPort: 8080, cidrBlocks: ["10.0.0.0/8"] }, // Internal metrics
    ],
    egress: [
        { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] },
    ],
});

// Deep Learning AMI (Ubuntu)
const ami = aws.ec2.getAmi({
    filters: [
        { name: "name", values: ["Deep Learning AMI (Ubuntu 20.04) Version*"] },
    ],
    owners: ["amazon"],
    mostRecent: true,
});

// Launch Template for Spot Instances
const launchTemplate = new aws.ec2.LaunchTemplate("cml-spot-template", {
    imageId: ami.then(a => a.id),
    instanceType: instanceType,
    vpcSecurityGroupIds: [sg.id],
    userData: Buffer.from(`#!/bin/bash
# Install CML Runner
curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
npm install -g @iterative/cml
# Start runner pointing to GitLab/GitHub
cml runner --repo=$REPO_URL --token=$RUNNER_TOKEN --labels=cml,gpu
`).toString('base64'),
});

// Request Spot Instances
const spotFleet = new aws.ec2.SpotFleetRequest("cml-spot-fleet", {
    targetCapacity: 1,
    iamFleetRole: "arn:aws:iam::123456789012:role/aws-ec2-spot-fleet-tagging-role", // Placeholder ARN
    launchTemplateConfigs: [{
        launchTemplateSpecification: {
            id: launchTemplate.id,
            version: "$Latest",
        },
    }],
    spotPrice: "0.50", // Max price
    terminateInstancesWithExpiration: true,
});

export const spotFleetId = spotFleet.id;
