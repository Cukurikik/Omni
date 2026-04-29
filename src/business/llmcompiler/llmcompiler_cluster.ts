import * as pulumi from "@pulumi/pulumi";
import * as kubernetes from "@pulumi/kubernetes";

// LLMCompiler distributed cluster config

const maxWorkerNodes = 50;

export function deployCompilerCluster(nodeCount: number) {
    if (nodeCount > maxWorkerNodes) {
        throw new Error(`Node count exceeds quota of ${maxWorkerNodes}`);
    }

    const appLabels = { app: "llmcompiler-worker" };
    const deployment = new kubernetes.apps.v1.Deployment("llmcompiler", {
        spec: {
            replicas: nodeCount,
            selector: { matchLabels: appLabels },
            template: {
                metadata: { labels: appLabels },
                spec: {
                    containers: [{
                        name: "worker",
                        image: "omni/llmcompiler:latest",
                        resources: {
                            limits: { cpu: "4", memory: "8Gi" }
                        }
                    }]
                }
            }
        }
    });

    return deployment.metadata.name;
}
