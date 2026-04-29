// Omni LLM7 Gateway Infra (Pulumi TS)
// Infrastructure Layer: Multi-provider gateway provisioning.
// Ref: chigwell/llm7.io
import * as aws from "@pulumi/aws";
const llm7Service = new aws.ecs.Service("OmniLLM7Gateway", {
    cluster: "omni-cluster",
    desiredCount: 3,
    tags: { Name: "Omni-LLM7-Gateway", Framework: "LLVM-Omni" },
});
export const serviceArn = llm7Service.id;
