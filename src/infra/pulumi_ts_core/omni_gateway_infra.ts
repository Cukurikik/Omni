// Omni Gateway Infra (Pulumi TS)
// Infrastructure Layer: AI Gateway load balancer provisioning.
// Ref: missingstudio/gateway

import * as aws from "@pulumi/aws";

const gatewayLb = new aws.lb.LoadBalancer("OmniGatewayLB", {
    loadBalancerType: "application",
    tags: { Name: "Omni-AI-Gateway", Framework: "LLVM-Omni" },
});

export const lbArn = gatewayLb.arn;
