import * as pulumi from "@pulumi/pulumi";
import * as awsx from "@pulumi/awsx";
import * as eks from "@pulumi/eks";

// Create a VPC for our cluster.
const vpc = new awsx.ec2.Vpc("omni-vpc", { numberOfAvailabilityZones: 3 });

// Create the EKS cluster and a managed node group with GPU instances.
const cluster = new eks.Cluster("omni-nexus-cluster", {
    vpcId: vpc.id,
    subnetIds: vpc.publicSubnetIds,
    instanceType: "t3.medium",
    desiredCapacity: 2,
    minSize: 1,
    maxSize: 3,
    createOidcProvider: true,
});

// Add a GPU node group for OMNI LLM inference
const gpuNodeGroup = new eks.ManagedNodeGroup("omni-gpu-nodes", {
    cluster: cluster,
    instanceTypes: ["g4dn.xlarge"], // NVIDIA T4
    scalingConfig: {
        desiredSize: 1,
        minSize: 1,
        maxSize: 5,
    },
    labels: { "omni-role": "inference" },
    taints: [{
        key: "nvidia.com/gpu",
        value: "true",
        effect: "NO_SCHEDULE",
    }],
});

// Export the cluster's kubeconfig.
export const kubeconfig = cluster.kubeconfig;
