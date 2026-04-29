import * as pulumi from "@pulumi/pulumi";
import * as k8s from "@pulumi/kubernetes";

// OMNI Infrastructure Layer: Pulumi Deployment for SQLFlow
// Sets up the parser, submitter, and MySQL backend inside Kubernetes.

const config = new pulumi.Config();
const namespaceName = config.get("namespace") || "omni-sqlflow";

const ns = new k8s.core.v1.Namespace("sqlflow-ns", {
    metadata: { name: namespaceName },
});

// SQLFlow Server Deployment
const sqlflowLabels = { app: "sqlflow-server" };
const sqlflowDeployment = new k8s.apps.v1.Deployment("sqlflow-server", {
    metadata: { namespace: ns.metadata.name },
    spec: {
        replicas: 3,
        selector: { matchLabels: sqlflowLabels },
        template: {
            metadata: { labels: sqlflowLabels },
            spec: {
                containers: [{
                    name: "sqlflow",
                    image: "sqlflow/sqlflow:latest",
                    ports: [{ containerPort: 50051 }],
                    env: [
                        { name: "SQLFLOW_MYSQL_HOST", value: "mysql-service" },
                        { name: "SQLFLOW_MYSQL_PORT", value: "3306" }
                    ],
                    resources: {
                        requests: { cpu: "500m", memory: "1Gi" },
                        limits: { cpu: "2", memory: "4Gi" }
                    }
                }],
            },
        },
    },
});

const sqlflowService = new k8s.core.v1.Service("sqlflow-service", {
    metadata: { namespace: ns.metadata.name },
    spec: {
        type: "ClusterIP",
        ports: [{ port: 50051, targetPort: 50051 }],
        selector: sqlflowLabels,
    },
});

export const sqlflowClusterIp = sqlflowService.spec.clusterIP;
