import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// OMNI ML Serving Infrastructure setup
// Strict typing and zero mock deployments

const config = new pulumi.Config();
const vpcId = config.get("vpcId") || aws.ec2.getVpc({ default: true }).then(v => v.id);

const cluster = new aws.ecs.Cluster("omni-ml-serving-cluster", {
    capacityProviders: ["FARGATE", "FARGATE_SPOT"],
    settings: [
        {
            name: "containerInsights",
            value: "enabled",
        },
    ],
});

// Create an IAM role for the task execution
const taskExecRole = new aws.iam.Role("omni-task-exec-role", {
    assumeRolePolicy: aws.iam.assumeRolePolicyForPrincipal({ Service: "ecs-tasks.amazonaws.com" }),
});

new aws.iam.RolePolicyAttachment("omni-task-exec-policy", {
    role: taskExecRole.name,
    policyArn: "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
});

// S3 access for pulling model artifacts
new aws.iam.RolePolicy("omni-s3-model-access", {
    role: taskExecRole.name,
    policy: {
        Version: "2012-10-17",
        Statement: [{
            Action: ["s3:GetObject", "s3:ListBucket"],
            Effect: "Allow",
            Resource: ["arn:aws:s3:::omni-model-registry/*", "arn:aws:s3:::omni-model-registry"]
        }],
    },
});

export const clusterName = cluster.name;
export const clusterArn = cluster.arn;
