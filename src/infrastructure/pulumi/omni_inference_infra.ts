import * as pulumi from "@pulumi/pulumi";
import * as k8s from "@pulumi/kubernetes";

const config = new pulumi.Config("omni");
const modelName = config.require("modelName");
const replicas = config.getNumber("replicas") ?? 3;
const modelImage = config.require("modelImage");
const ns = "omni-inference";

const deployment = new k8s.apps.v1.Deployment("inference", {
    metadata: { name: `${modelName}-inference`, namespace: ns },
    spec: {
        replicas,
        selector: { matchLabels: { app: "omni-inference", model: modelName } },
        template: {
            metadata: { labels: { app: "omni-inference", model: modelName } },
            spec: {
                containers: [{
                    name: "inference", image: modelImage,
                    ports: [{ containerPort: 8080, name: "grpc" }],
                    resources: {
                        requests: { cpu: "4", memory: "16Gi", "nvidia.com/gpu": "1" },
                        limits: { cpu: "8", memory: "32Gi", "nvidia.com/gpu": "1" },
                    },
                    readinessProbe: { httpGet: { path: "/health", port: 8081 }, initialDelaySeconds: 60 },
                }],
            },
        },
    },
});

const svc = new k8s.core.v1.Service("svc", {
    metadata: { name: `${modelName}-svc`, namespace: ns },
    spec: {
        selector: { app: "omni-inference", model: modelName },
        ports: [{ port: 8080, targetPort: 8080 }],
    },
}, { dependsOn: deployment });

export const endpoint = pulumi.interpolate`${svc.metadata.name}.${ns}.svc.cluster.local:8080`;
