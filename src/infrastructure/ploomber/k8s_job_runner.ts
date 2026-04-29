import * as pulumi from "@pulumi/pulumi";
import * as k8s from "@pulumi/kubernetes";

// OMNI Ploomber - Kubernetes Job Runner
// IaC for deploying isolated Ploomber DAG tasks as Kubernetes Jobs

export class PloomberTaskJob {
    public readonly jobName: pulumi.Output<string>;

    constructor(name: string, namespace: string, image: string, command: string[], memoryLimit: string = "1Gi") {
        const job = new k8s.batch.v1.Job(`${name}-job`, {
            metadata: {
                namespace: namespace,
                name: `${name}-job`,
                labels: {
                    "omni.ploomber/task": name,
                }
            },
            spec: {
                backoffLimit: 3, // Retry policy
                activeDeadlineSeconds: 3600, // 1 hour max SLA timeout
                template: {
                    metadata: {
                        labels: {
                            "omni.ploomber/task": name,
                        }
                    },
                    spec: {
                        restartPolicy: "Never",
                        containers: [{
                            name: "task-runner",
                            image: image,
                            command: command,
                            resources: {
                                limits: {
                                    memory: memoryLimit,
                                    cpu: "1000m",
                                },
                                requests: {
                                    memory: "256Mi",
                                    cpu: "200m",
                                }
                            },
                            env: [
                                {
                                    name: "OMNI_DAG_EXECUTION_CONTEXT",
                                    value: "k8s-job"
                                }
                            ]
                        }]
                    }
                }
            }
        });

        this.jobName = job.metadata.name;
    }
}
