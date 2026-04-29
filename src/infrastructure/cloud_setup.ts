// OMNI Infrastructure Layer - Pulumi TypeScript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// OMNI Unikernel Cloud Deployment Infrastructure
export const deployOmniUnikernel = () => {
    // Defines an AWS Firecracker microVM execution environment for OMNI
    const omniInstance = new aws.ec2.Instance("omni-core-node", {
        ami: "ami-omni-unikernel-optimized", // Custom OMNI AMI
        instanceType: "c7g.medium", // Graviton for high performance
        tags: {
            Environment: "Production",
            OmniLayer: "Infrastructure",
        },
    });

    return {
        instanceId: omniInstance.id,
        publicIp: omniInstance.publicIp,
    };
};
