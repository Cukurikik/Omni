import * as k8s from "@pulumi/kubernetes";

const servingDeployment = new k8s.apps.v1.Deployment("bentoml-serving", {
    spec: {
        replicas: 3,
        selector: { matchLabels: { app: "bentoml-serving" } },
        template: {
            metadata: { labels: { app: "bentoml-serving" } },
            spec: {
                containers: [{
                    name: "serving-container",
                    image: "omni-bentoml:latest",
                    ports: [{ containerPort: 3000 }]
                }]
            }
        }
    }
});
