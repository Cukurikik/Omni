// Omni ChatFAQ Infra (Pulumi TS)
// Infrastructure Layer: Conversational AI service provisioning.
// Ref: ChatFAQ/ChatFAQ
import * as aws from "@pulumi/aws";
const chatfaqService = new aws.ecs.Service("OmniChatFAQService", {
    cluster: "omni-cluster",
    desiredCount: 2,
    tags: { Name: "Omni-ChatFAQ", Framework: "LLVM-Omni" },
});
export const serviceArn = chatfaqService.id;
