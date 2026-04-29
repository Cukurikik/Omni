import * as aws from "@pulumi/aws";
import * as pulumi from "@pulumi/pulumi";

// AWS ECS GPU Cluster for Training
const vpc = new aws.ec2.Vpc("omni-gpu-vpc", { cidrBlock: "10.0.0.0/16" });

const cluster = new aws.ecs.Cluster("omni-gpu-cluster", {
    settings: [{ name: "containerInsights", value: "enabled" }]
});

// Assuming a specific GPU instance type
const capacityProvider = new aws.ecs.CapacityProvider("gpu-cp", {
    autoScalingGroupProvider: {
        autoScalingGroupArn: "arn:aws:autoscaling:region:account:autoScalingGroup:id:autoScalingGroupName/asg",
        managedScaling: { status: "ENABLED" }
    }
});
