import * as aws from "@pulumi/aws";
import * as eks from "@pulumi/eks";

// Deploying Aim Stack tracking server onto Kubernetes
const aimDeployment = new eks.Deployment("aim-tracker", {
    spec: {
        replicas: 2,
        selector: { matchLabels: { app: "aim" } },
        template: {
            metadata: { labels: { app: "aim" } },
            spec: {
                containers: [{
                    name: "aim-server",
                    image: "aimhubio/aim:latest",
                    ports: [{ containerPort: 43800 }],
                    command: ["aim", "server", "--host", "0.0.0.0"]
                }]
            }
        }
    }
});
