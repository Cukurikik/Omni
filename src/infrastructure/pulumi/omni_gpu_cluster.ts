// OMNI Infrastructure — Pulumi GPU Cluster Deployment
// TypeScript-based infrastructure as code for Kubernetes GPU cluster.

import * as pulumi from "@pulumi/pulumi";
import * as k8s from "@pulumi/kubernetes";

const config = new pulumi.Config();
const clusterName = config.get("clusterName") || "omni-inference";
const gpuNodeCount = config.getNumber("gpuNodes") || 3;
const gpuType = config.get("gpuType") || "nvidia-a100";
const modelImage = config.get("modelImage") || "omni/inference-server:latest";
const replicas = config.getNumber("replicas") || 3;

// GPU Node Pool (reference to existing cluster)
const namespace = new k8s.core.v1.Namespace("omni-inference", {
    metadata: { name: "omni-inference", labels: { app: "omni", tier: "inference" } },
});

// GPU Resource Quota
const quota = new k8s.core.v1.ResourceQuota("gpu-quota", {
    metadata: { namespace: namespace.metadata.name },
    spec: {
        hard: {
            "nvidia.com/gpu": "8",
            "requests.cpu": "64",
            "requests.memory": "256Gi",
        },
    },
});

// Model Weights PVC
const modelStorage = new k8s.core.v1.PersistentVolumeClaim("model-weights", {
    metadata: { namespace: namespace.metadata.name },
    spec: {
        accessModes: ["ReadOnlyMany"],
        resources: { requests: { storage: "100Gi" } },
        storageClassName: "ssd-retain",
    },
});

// Inference Deployment
const inferenceDeployment = new k8s.apps.v1.Deployment("omni-inference", {
    metadata: { namespace: namespace.metadata.name },
    spec: {
        replicas: replicas,
        selector: { matchLabels: { app: "omni-inference" } },
        template: {
            metadata: { labels: { app: "omni-inference" } },
            spec: {
                containers: [{
                    name: "inference",
                    image: modelImage,
                    ports: [{ containerPort: 8080, name: "http" }, { containerPort: 50051, name: "grpc" }],
                    resources: {
                        requests: { cpu: "4", memory: "16Gi", "nvidia.com/gpu": "1" },
                        limits: { cpu: "8", memory: "32Gi", "nvidia.com/gpu": "1" },
                    },
                    env: [
                        { name: "MODEL_ID", value: "omni-7b" },
                        { name: "MAX_BATCH_SIZE", value: "32" },
                        { name: "NUM_WORKERS", value: "4" },
                    ],
                    volumeMounts: [{ name: "model-weights", mountPath: "/models", readOnly: true }],
                    livenessProbe: { httpGet: { path: "/health", port: 8080 }, initialDelaySeconds: 30, periodSeconds: 10 },
                    readinessProbe: { httpGet: { path: "/ready", port: 8080 }, initialDelaySeconds: 15, periodSeconds: 5 },
                }],
                volumes: [{ name: "model-weights", persistentVolumeClaim: { claimName: modelStorage.metadata.name } }],
                tolerations: [{ key: "nvidia.com/gpu", operator: "Exists", effect: "NoSchedule" }],
            },
        },
    },
});

// Service
const service = new k8s.core.v1.Service("omni-inference-svc", {
    metadata: { namespace: namespace.metadata.name },
    spec: {
        selector: { app: "omni-inference" },
        ports: [
            { name: "http", port: 80, targetPort: 8080 },
            { name: "grpc", port: 50051, targetPort: 50051 },
        ],
        type: "ClusterIP",
    },
});

// HPA for auto-scaling
const hpa = new k8s.autoscaling.v2.HorizontalPodAutoscaler("omni-hpa", {
    metadata: { namespace: namespace.metadata.name },
    spec: {
        scaleTargetRef: {
            apiVersion: "apps/v1", kind: "Deployment",
            name: inferenceDeployment.metadata.name,
        },
        minReplicas: 1, maxReplicas: 10,
        metrics: [
            { type: "Resource", resource: { name: "cpu", target: { type: "Utilization", averageUtilization: 70 } } },
            { type: "Resource", resource: { name: "nvidia.com/gpu", target: { type: "Utilization", averageUtilization: 80 } } },
        ],
    },
});

export const namespaceName = namespace.metadata.name;
export const serviceEndpoint = service.metadata.name;
export const deploymentName = inferenceDeployment.metadata.name;
