// Omni Auffusion Infra (Pulumi TypeScript)
// Infrastructure Layer: Provisioning dedicated instances for audio diffusion.

import * as aws from "@pulumi/aws";

// Deterministic EC2 provisioning for Auffusion Audio Generation Model
const auffusionGpuInstance = new aws.ec2.Instance("OmniAuffusionGpuNode", {
    ami: "ami-0c55b159cbfafe1f0", // Omni LLM Base AMI
    instanceType: "g4dn.xlarge", // Audio diffusion bounds
    tags: {
        Name: "Omni-Auffusion-Engine",
        Layer: "Compute",
        Framework: "LLVM-Omni",
    },
});

export const instanceId = auffusionGpuInstance.id;
export const instancePublicIp = auffusionGpuInstance.publicIp;
