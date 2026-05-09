// OMNI Infra Layer: Pulumi K8s
import * as k8s from "@pulumi/kubernetes";
const appLabels = { app: "omni" };
const deployment = new k8s.apps.v1.Deployment("omni-dep", {
    spec: { selector: { matchLabels: appLabels }, template: { metadata: { labels: appLabels } } }
});
