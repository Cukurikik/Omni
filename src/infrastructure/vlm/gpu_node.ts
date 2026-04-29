import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const gpuInstance = new aws.ec2.Instance("omni-vlm-gpu", {
    instanceType: "p3.2xlarge",
    ami: "ami-0abcdef1234567890",
});

export const instanceId = gpuInstance.id;
