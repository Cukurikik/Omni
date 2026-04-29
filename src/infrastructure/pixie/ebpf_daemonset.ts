import * as k8s from "@pulumi/kubernetes";

const pixieDaemonSet = new k8s.apps.v1.DaemonSet("pixie-ebpf", {
    metadata: { namespace: "px-operator" },
    spec: {
        selector: { matchLabels: { app: "pixie-vizier" } },
        template: {
            metadata: { labels: { app: "pixie-vizier" } },
            spec: {
                hostPID: true,
                containers: [{
                    name: "vizier-pem",
                    image: "pixie-oss/pixie-pem:latest",
                    securityContext: { privileged: true },
                }],
            },
        },
    },
});
