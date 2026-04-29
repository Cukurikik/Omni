import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// OMNI TEXT-GENERATION-WEBUI: Container Stack
// Pulumi script simulating a docker-compose setup using AWS ECS to run the Oobabooga web interface and backend.
// Source: oobabooga/text-generation-webui

const config = new pulumi.Config();
const stackName = "omni-text-webui";

// 1. Cluster
const cluster = new aws.ecs.Cluster(`${stackName}-cluster`, {});

// 2. Task Definition (Frontend + Backend in same task or networked)
const taskDefinition = new aws.ecs.TaskDefinition(`${stackName}-task`, {
    family: "text-generation-webui",
    cpu: "4096", // 4 vCPU
    memory: "16384", // 16GB RAM
    networkMode: "awsvpc",
    requiresCompatibilities: ["FARGATE"], // Using Fargate for simplicity in Pulumi, though usually needs EC2+GPU
    executionRoleArn: aws.iam.Role.get("ecsExecutionRole", "ecsTaskExecutionRole").arn,
    containerDefinitions: JSON.stringify([
        {
            name: "webui",
            image: "atinoda/text-generation-webui:latest",
            portMappings: [
                { containerPort: 7860, hostPort: 7860, protocol: "tcp" }, // Gradio Web UI
                { containerPort: 5000, hostPort: 5000, protocol: "tcp" }  // API
            ],
            environment: [
                { name: "CLI_ARGS", value: "--listen --api" }
            ],
            essential: true,
            logConfiguration: {
                logDriver: "awslogs",
                options: {
                    "awslogs-group": `/ecs/${stackName}`,
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "webui"
                }
            }
        }
    ]),
});

export const clusterArn = cluster.arn;
export const taskDefArn = taskDefinition.arn;
