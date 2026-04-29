import * as aws from "@pulumi/aws";

// K8s cluster for Agent Squad Swarm
const agentCluster = new aws.eks.Cluster("agent-squad-cluster", {
    roleArn: "arn:aws:iam::account:role/eksRole",
    vpcConfig: {
        subnetIds: ["subnet-123", "subnet-456"],
    },
});
