import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// OMNI ALGOWIKI: Algorithm Benchmarking Cluster
// Provisions isolated Kubernetes nodes specifically for highly-concurrent algorithm performance testing.
// Source: vicky002/AlgoWiki

const config = new pulumi.Config();
const clusterName = "omni-algo-benchmark";

// IAM Roles for EKS
const eksRole = new aws.iam.Role(`${clusterName}-eksRole`, {
    assumeRolePolicy: aws.iam.assumeRolePolicyForPrincipal({ Service: "eks.amazonaws.com" }),
});
const nodeGroupRole = new aws.iam.Role(`${clusterName}-nodegroupRole`, {
    assumeRolePolicy: aws.iam.assumeRolePolicyForPrincipal({ Service: "ec2.amazonaws.com" }),
});

// Setup VPC for isolation
const vpc = new aws.ec2.Vpc(`${clusterName}-vpc`, {
    cidrBlock: "10.100.0.0/16",
    enableDnsHostnames: true,
});

// Create EKS Cluster
const cluster = new aws.eks.Cluster(clusterName, {
    roleArn: eksRole.arn,
    vpcConfig: {
        subnetIds: [], // Omitted subnet creation for brevity
    },
});

// Create Compute-Optimized Node Group (c6i instances for pure algorithmic throughput)
const nodeGroup = new aws.eks.NodeGroup(`${clusterName}-ng`, {
    clusterName: cluster.name,
    nodeRoleArn: nodeGroupRole.arn,
    subnetIds: [], // Omitted for brevity
    scalingConfig: {
        desiredSize: 2,
        maxSize: 5,
        minSize: 1,
    },
    instanceTypes: ["c6i.2xlarge"], // Intel Ice Lake, great for C++ algos
});

export const kubeconfig = pulumi.all([cluster.name, cluster.endpoint, cluster.certificateAuthority]).apply(([name, endpoint, ca]) => {
    return `apiVersion: v1
clusters:
- cluster:
    server: ${endpoint}
    certificate-authority-data: ${ca.data}
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: aws
  name: aws
current-context: aws
kind: Config
preferences: {}
users:
- name: aws
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: aws-iam-authenticator
      args:
        - "token"
        - "-i"
        - "${name}"
`;
});
