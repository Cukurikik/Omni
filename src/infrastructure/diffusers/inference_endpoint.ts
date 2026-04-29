import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// OMNI DIFFUSERS: Inference Endpoint
// Provisions an AWS SageMaker Endpoint to host HuggingFace Diffusers for scalable image generation.
// Source: huggingface/diffusers

const config = new pulumi.Config();
const deploymentName = "omni-diffusers-sdxl";

// SageMaker Execution Role
const sagemakerRole = new aws.iam.Role(`${deploymentName}-role`, {
    assumeRolePolicy: JSON.stringify({
        Version: "2012-10-17",
        Statement: [{
            Action: "sts:AssumeRole",
            Principal: { Service: "sagemaker.amazonaws.com" },
            Effect: "Allow",
        }],
    }),
});

// Attach policies
new aws.iam.RolePolicyAttachment(`${deploymentName}-attach-sagemaker`, {
    role: sagemakerRole.name,
    policyArn: "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
});

// Define the Model using a pre-built HuggingFace PyTorch Inference Container
const model = new aws.sagemaker.Model(`${deploymentName}-model`, {
    executionRoleArn: sagemakerRole.arn,
    primaryContainer: {
        // Deep Learning Container (DLC) for PyTorch
        image: "763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:2.0.0-transformers4.28.1-gpu-py310-cu118-ubuntu20.04",
        environment: {
            "HF_MODEL_ID": "stabilityai/stable-diffusion-xl-base-1.0",
            "HF_TASK": "text-to-image",
            "SAGEMAKER_CONTAINER_LOG_LEVEL": "20",
        },
    },
});

// Endpoint Configuration
const endpointConfig = new aws.sagemaker.EndpointConfiguration(`${deploymentName}-config`, {
    productionVariants: [{
        variantName: "AllTraffic",
        modelName: model.name,
        initialInstanceCount: 1,
        instanceType: "ml.g5.2xlarge", // A10G GPU for fast SDXL inference
        initialVariantWeight: 1.0,
    }],
});

// Deploy the Endpoint
const endpoint = new aws.sagemaker.Endpoint(`${deploymentName}-endpoint`, {
    endpointConfigName: endpointConfig.name,
});

export const sagemakerEndpointName = endpoint.name;
